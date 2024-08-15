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

class LanguagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguagesModel
        fields = ['id', 'name', 'code']  # یا هر فیلد دیگری که نیاز دارید


class CompressorSettingSerializer(serializers.ModelSerializer):
    channels = ChannelsSerializer(many=True, read_only=True)
    ads = AdsSerializer(many=True, read_only=True)
    bot = BotsSerializer(read_only=True)
    plans = serializers.SerializerMethodField()
    texts = serializers.SerializerMethodField()
    langs = serializers.SerializerMethodField()
    admin = serializers.SerializerMethodField()  # Field for admin users

    class Meta:
        model = CompressorSettingModel
        fields = '__all__'

    def get_plans(self, obj):
        plans = CompressorPlansModel.objects.filter(bot=obj.bot)
        return CompressorPlansSerializer(plans, many=True).data

    def get_texts(self, obj):
        lang_code = self.context.get('lang_code')

        if lang_code:
            try:
                lang = LanguagesModel.objects.get(code=lang_code)
            except LanguagesModel.DoesNotExist:
                lang = None
        else:
            lang = None
        
        if lang:
            try:
                texts = CompressorTextModel.objects.get(bot=obj.bot, lang=lang)
            except CompressorTextModel.DoesNotExist:
                texts = CompressorTextModel.objects.filter(bot=obj.bot).first()
        else:
            texts = CompressorTextModel.objects.filter(bot=obj.bot).first()

        if not texts:
            return {}

        return CompressorTextSerializer(texts).data

    def get_langs(self, obj):
        language_ids = obj.langs.all()
        languages = LanguagesModel.objects.filter(id__in=language_ids)
        return LanguagesSerializer(languages, many=True).data

    def get_admin(self, obj):
        # Get all users who are admin
        admin_users = User.objects.filter(is_admin=True)
        return UserSerializer(admin_users, many=True).data




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['chat_id', 'full_name', 'wallet', 'phone', 'is_admin', 'is_active', 'creation']








class CompressorUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nested serializer for user information
    plan = CompressorPlansSerializer()  # Nested serializer for plan details
    lang = serializers.SlugRelatedField(queryset=LanguagesModel.objects.all(), slug_field='code', required=False)  # Use code instead of id
    quality = serializers.ChoiceField(choices=[('quality_0', 'Quality 0'), ('quality_1', 'Quality 1'), ('quality_2', 'Quality 2'), ('quality_3', 'Quality 3')], required=False, allow_null=True)

    class Meta:
        model = CompressorUser
        fields = ['user', 'plan', 'bot', 'lang', 'expiry', 'volume', 'quality']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        plan_data = validated_data.pop('plan', None)
        user = instance.user

        # Update user fields
        for attr, value in user_data.items():
            if hasattr(user, attr):
                setattr(user, attr, value)
        user.save()

        # Update plan if provided
        if plan_data:
            plan = CompressorPlansModel.objects.get(pk=plan_data['id'])
            instance.plan = plan

        # Update CompressorUser fields
        for attr, value in validated_data.items():
            if hasattr(instance, attr):
                setattr(instance, attr, value)
        instance.save()

        return instance
