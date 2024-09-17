from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from compressor.models import CompressorUser
from .serializers import CompressorUserSerializer
from core.models import BotsModel
from django.shortcuts import get_object_or_404 , render
from . import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import BotsModel, LanguagesModel
from .serializers import CompressorSettingSerializer
from rest_framework.response import Response
from core.tasks import send_message
from .models import  User , UserPaymentModel
import requests
from django.conf import settings
from compressor.models import CompressorPlansModel , CompressorUser
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import BotsModel,LanguagesModel
from compressor.models import CompressorSettingModel , CompressorTextModel 
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _






sandbox = 'sandbox' if settings.DEBUG else 'www'
ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"
CallbackURL = 'http://127.0.0.1:8000/api/verify/'



@method_decorator(csrf_exempt, name='dispatch')
class PaymentCreateView(APIView):
    def post(self, request):
        amount = request.data.get('amount')
        chat_id = request.data.get('chat_id')
        plan_id = request.data.get('plan_id')
        bot_id = request.data.get('bot_id')


        try:
            bot = BotsModel.objects.get(id = bot_id)
            user = User.objects.get(chat_id = chat_id)

            
            if bot.type == 'compressor' :
                setting = CompressorSettingModel.objects.first()
            
            
            data = {
                "MerchantID": setting.zarin_key,
                "Amount": int(amount),
                "Description":'klh',
                "Phone": '09123456789',
                "CallbackURL": CallbackURL,
            }
            data = json.dumps(data)
            headers = {'content-type': 'application/json', 'content-length': str(len(data))}

            response = requests.post(ZP_API_REQUEST, data=data, headers=headers, timeout=10)

            if response.status_code == 200:
                response_data = response.json()

                if response_data['Status'] == 100:
                    UserPaymentModel.objects.create(
                        user=user,
                        bot = bot,
                        amount=amount,
                        key=str(response_data['Authority']),
                        plan=plan_id,
                    )
                    return Response({
                        'status': True,
                        'url': ZP_API_STARTPAY + str(response_data['Authority']),
                        'authority': response_data['Authority']
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({'status': False, 'code': str(response_data['Status'])}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'status': False, 'code': 'unexpected error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except User.DoesNotExist:
            return Response({'status': False, 'code': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        except requests.exceptions.Timeout:
            return Response({'status': False, 'code': 'timeout'}, status=status.HTTP_408_REQUEST_TIMEOUT)
        except requests.exceptions.ConnectionError:
            return Response({'status': False, 'code': 'connection error'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)




class PaymentVerifyView(APIView):

    def get(self, request):
        authority = request.GET.get('Authority')

        try:
            payment_data = UserPaymentModel.objects.get(key=authority)
            setting = payment_data.bot.setting
            if authority:
                data = {
                    "MerchantID": setting.zarin_key,
                    "Amount": int(payment_data.amount),
                    "Authority": authority,
                }
                data = json.dumps(data)
                headers = {'content-type': 'application/json', 'content-length': str(len(data))}
                response = requests.post(ZP_API_VERIFY, data=data, headers=headers)

                if response.status_code == 200:
                    response_data = response.json()

                    if response_data['Status'] == 100:
                        # Update payment status
                        payment_data.status = True
                        payment_data.save()

                        # Find the user and bot
                        user = payment_data.user
                        bot = payment_data.bot

                        if bot.type == 'compressor':
                            # Handle compressor bot
                            try:
                                plan = CompressorPlansModel.objects.get(id=payment_data.plan)

                                compressor_user, created = CompressorUser.objects.get_or_create(user=user)
                                compressor_user.plan = plan

                                compressor_user.save()

                            except CompressorPlansModel.DoesNotExist:
                                return Response({'status': 'failure', 'code': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)

                        # Redirect to success page
                        text = f'✅ پرداخت شما با موفقیت انجام شد و پلن {plan.name} برای شما فعال شد .'
                        send_message.delay_on_commit(chat_id = payment_data.user.chat_id ,bot_id = payment_data.bot.id , text = text)
                        return render(request, 'core/success.html')

                    else:
                        # Payment verification failed
                        payment_data.status = False
                        payment_data.save()
                        return render(request, 'core/unsuccess.html')

                return Response({'status': 'failure', 'code': 'unexpected error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'status': 'failure', 'code': 'authority missing'}, status=status.HTTP_400_BAD_REQUEST)

        except UserPaymentModel.DoesNotExist:
            return Response({'status': 'failure', 'code': 'payment not found'}, status=status.HTTP_404_NOT_FOUND)








class SettingsAPIView(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        bot_username = request.data.get('bot')
        lang_code = request.data.get('lang')

        if not bot_username:
            return Response({"detail": _("Bot username is required.")}, status=status.HTTP_400_BAD_REQUEST)
        
        bot = get_object_or_404(BotsModel, username=bot_username)

        try:
            settings = CompressorSettingModel.objects.get(bot=bot)
        except CompressorSettingModel.DoesNotExist:
            return Response({"detail": _("Settings not found for the specified bot.")}, status=status.HTTP_404_NOT_FOUND)

        serializer = CompressorSettingSerializer(settings, context={'lang_code': lang_code})

        return Response(serializer.data, status=status.HTTP_200_OK)





class UserAPIView(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        chat_id = request.data.get('chat_id')
        full_name = request.data.get('full_name')
        plan_id = request.data.get('plan')
        expiry = request.data.get('expiry')
        volume = request.data.get('volume')
        is_active = request.data.get('is_active')
        quality = request.data.get('quality')
        language_code = request.data.get('lang')  # دریافت کد زبان
        bot_id = request.data.get('bot')  # دریافت شناسه ربات
        bot_type = request.data.get('type')

        if not chat_id or not bot_type:
            return Response({"error": "chat_id and bot_type are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve or create the User
        user, user_created = User.objects.get_or_create(chat_id=chat_id, defaults={'full_name': full_name})

        if not user_created:
            # Update user information if it already exists
            if full_name:
                user.full_name = full_name
            if 'wallet' in request.data:
                user.wallet = request.data.get('wallet')
            if 'phone' in request.data:
                user.phone = request.data.get('phone')
            if is_active is not None:
                user.is_active = is_active
            user.save()

        if bot_type == 'compressor':
            # Retrieve or create the CompressorUser
            compressor_user, created = CompressorUser.objects.get_or_create(user=user)

            # Update the CompressorUser information
            if plan_id:
                plan = CompressorPlansModel.objects.filter(id=plan_id).first()
                if plan:
                    compressor_user.plan = plan
            if expiry:
                compressor_user.expiry = expiry
            if volume is not None:
                compressor_user.volume = volume
            if quality:
                compressor_user.quality = quality
            if language_code:
                language = LanguagesModel.objects.filter(code=language_code).first()
                if language:
                    compressor_user.lang = language
            if bot_id:
                bot = BotsModel.objects.filter(id=bot_id).first()
                if bot:
                    compressor_user.bot = bot

            compressor_user.save()
            serializer = CompressorUserSerializer(compressor_user)
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid bot type"}, status=status.HTTP_400_BAD_REQUEST)
