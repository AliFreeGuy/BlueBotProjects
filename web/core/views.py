from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import BotsModel
from django.shortcuts import get_object_or_404 , render
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from core.tasks import send_message
from .models import  User , UserPaymentModel
from compressor.models import CompressorUser  , CompressorPlansModel,CompressorSettingModel
import requests
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json





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






