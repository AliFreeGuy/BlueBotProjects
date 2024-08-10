from rest_framework import serializers
from compressor.models import CompressorSettingModel   , CompressorPlansModel , CompressorTextModel , CompressorUser
from core.models import ChannelsModel , AdsModels  ,BotsModel , LanguagesModel
from accounts.models import User




class CompressorUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompressorUser
        fields = '__all__'  




class ChannelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelsModel
        fields = '__all__'

class AdsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdsModels
        fields = '__all__'

class BotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotsModel
        fields = '__all__'

class CompressorPlansSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompressorPlansModel
        fields = '__all__'


class CompressorTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompressorTextModel
        fields = '__all__'



class CompressorSettingSerializer(serializers.ModelSerializer):
    channels = ChannelsSerializer(many=True, read_only=True)
    ads = AdsSerializer(many=True, read_only=True)
    bot = BotsSerializer(read_only=True)  # Assuming a relationship between setting and bot
    plans = serializers.SerializerMethodField()  # Custom method to include plans
    texts = serializers.SerializerMethodField()  # Custom method to include texts

    class Meta:
        model = CompressorSettingModel
        fields = '__all__'

    def get_plans(self, obj):
        plans = CompressorPlansModel.objects.filter(bot=obj.bot)
        return CompressorPlansSerializer(plans, many=True).data

    def get_texts(self, obj):
        # Get the language code from context (if available)
        lang_code = self.context.get('lang_code')

        # Try to get the language object
        if lang_code:
            try:
                lang = LanguagesModel.objects.get(code=lang_code)
            except LanguagesModel.DoesNotExist:
                lang = None
        else:
            lang = None
        
        # Attempt to get the texts for the given bot and language
        if lang:
            try:
                texts = CompressorTextModel.objects.get(bot=obj.bot, lang=lang)
            except CompressorTextModel.DoesNotExist:
                # If texts for the specific lang do not exist, get the first available text
                texts = CompressorTextModel.objects.filter(bot=obj.bot).first()
        else:
            # If no lang is provided, get the first available text
            texts = CompressorTextModel.objects.filter(bot=obj.bot).first()

        # If no texts are found, return an empty dictionary
        if not texts:
            return {}

        return CompressorTextSerializer(texts).data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['chat_id', 'full_name', 'wallet', 'phone', 'is_admin', 'is_active', 'creation']

class CompressorUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nested serializer for user information
    plan = serializers.PrimaryKeyRelatedField(queryset=CompressorPlansModel.objects.all(), required=False)
    lang = serializers.SlugRelatedField(queryset=LanguagesModel.objects.all(), slug_field='code', required=False)  # Use code instead of id
    quality = serializers.ChoiceField(choices=[('quality_0', 'Quality 0'), ('quality_1', 'Quality 1'), ('quality_2', 'Quality 2'), ('quality_3', 'Quality 3')], required=False, allow_null=True)

    class Meta:
        model = CompressorUser
        fields = ['user', 'plan', 'bot', 'lang', 'expiry', 'volume', 'quality']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user

        # Update user fields
        for attr, value in user_data.items():
            if hasattr(user, attr):
                setattr(user, attr, value)
        user.save()

        # Update CompressorUser fields
        for attr, value in validated_data.items():
            if hasattr(instance, attr):
                setattr(instance, attr, value)
        instance.save()

        return instance