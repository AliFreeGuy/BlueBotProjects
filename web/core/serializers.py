from rest_framework import serializers
from compressor.models import CompressorSettingModel   , CompressorPlansModel , CompressorTextModel
from core.models import ChannelsModel , AdsModels  ,BotsModel , LanguagesModel



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
