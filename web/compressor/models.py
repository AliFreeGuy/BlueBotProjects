from django.db import models
from core.models import BaseBotSettingModel
from accounts.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from core.models import BotsModel , LanguagesModel
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _




class CompressorSettingModel(BaseBotSettingModel):
    max_limit_video = models.PositiveBigIntegerField()

    quality_1 =  models.IntegerField(default=1)
    quality_2 =  models.IntegerField(default=1)
    quality_3 = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Setting"
        verbose_name_plural = "Settings"




class CompressorPlansModel(models.Model):
    bot = models.ForeignKey(BotsModel , related_name='plans' , on_delete=models.CASCADE)
    tag = models.SlugField(max_length=128, unique=True, default='compressor')
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField()
    day = models.IntegerField(default=0)
    volume = models.IntegerField(default=0)
    price = models.PositiveBigIntegerField(default=0)

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Plans"





class CompressorUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='compressor')
    plan = models.ForeignKey(CompressorPlansModel, related_name='users', on_delete=models.SET_NULL, null=True, blank=True)
    bot = models.ForeignKey(BotsModel, on_delete=models.SET_NULL, null=True, blank=True)
    lang = models.ForeignKey(LanguagesModel, related_name='users', on_delete=models.SET_NULL, null=True, blank=True)
    expiry = models.DateTimeField(null=True, blank=True)
    volume = models.BigIntegerField(default=0, null=True, blank=True)
    quality = models.CharField(max_length=20, choices=[('quality_0', 'Quality 0'), ('quality_1', 'Quality 1'), ('quality_2', 'Quality 2'), ('quality_3', 'Quality 3')], blank=True, null=True)

    def __str__(self) -> str:
        return str(self.user)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def save(self, *args, **kwargs):
        if self.pk:
            # Fetch the existing instance if it exists
            existing_instance = CompressorUser.objects.get(pk=self.pk)

            if existing_instance.plan != self.plan:
                # If plan has changed, update volume and expiry
                if self.plan:
                    self.volume = self.plan.volume
                    self.expiry = timezone.now() + timezone.timedelta(days=self.plan.day)
                else:
                    # If plan is removed, clear volume and expiry
                    self.volume = 0
                    self.expiry = None

            # Check if the current subscription is expired
            if self.expiry and self.expiry < timezone.now():
                self.plan = None
                self.volume = 0
                self.expiry = None
                self.is_active = False
        else:
            # If this is a new instance and no plan is assigned, assign the free plan
            if not self.plan:
                try:
                    free_plan = CompressorPlansModel.objects.get(tag='free')
                    self.plan = free_plan
                    self.volume = free_plan.volume
                    self.expiry = timezone.now() + timezone.timedelta(days=free_plan.day)
                    self.is_active = True
                except CompressorPlansModel.DoesNotExist:
                    pass

            # Assign the compressor bot if not already assigned
            if not self.bot:
                try:
                    compressor_bot = BotsModel.objects.get(type='compressor')
                    self.bot = compressor_bot
                except BotsModel.DoesNotExist:
                    pass

        # Ensure volume and expiry are reset if no plan is assigned
        if not self.plan:
            self.volume = 0
            self.expiry = None
            self.is_active = False

            # Assign the free plan if it exists
            try:
                free_plan = CompressorPlansModel.objects.get(tag='free')
                self.plan = free_plan
                self.volume = free_plan.volume
                self.expiry = timezone.now() + timezone.timedelta(days=free_plan.day)
                self.is_active = True
            except CompressorPlansModel.DoesNotExist:
                pass

        # Set quality to 'quality_0' if not provided
        if not self.quality:
            self.quality = 'quality_0'

        # Save the instance
        super().save(*args, **kwargs)




class CompressorTextModel(models.Model):
    bot = models.ForeignKey(BotsModel, related_name='texts', on_delete=models.CASCADE)
    lang = models.OneToOneField(LanguagesModel, related_name='texts', on_delete=models.CASCADE)

    start_text = models.TextField(default='متن استارت')
    help_text = models.TextField(default='متن راهنما')
    rule_text = models.TextField(default='متن قوانین')
    support_text = models.TextField(default='متن پشتیبانی')
    bot_not_active_text = models.TextField(default='متن ربات غیر فعال')
    user_not_active_text = models.TextField(default='متن کاربر غیر فعال')
    user_not_sub_text = models.TextField(default='متن کاربر اشتراک ندارد')
    error_text = models.TextField(default='متن خطای غیر منتظره')
    sub_text = models.TextField(default='متن اشتراک‌ها')
    payment_gateway_text = models.TextField(default='متن درگاه پرداخت')
    payment_text = models.TextField(default='متن بخش وارد کردن مقدار شارژ حساب کاربر')
    payment_success_text = models.TextField(default='متن پرداخت موفق کاربر')
    force_join_text = models.TextField(default='متن جوین اجباری برای کانال')
    privacy_text = models.TextField(default='متن حریم خصوصی')
    user_not_join_text = models.TextField(default='متن کاربر هنوز در کانال عضو نیست')
    max_limit_payment_text = models.TextField(default='متن حداکثر شارژ حساب')
    setting_text = models.TextField(default='متن بخش تنظیمات ربات')
    user_profile_text = models.TextField(default='متن زیر اطلاعات پروفایل کاربر')
    user_ref_text = models.TextField(default='متن دعوت کاربر')
    placeholder_text = models.CharField(max_length=128 , default='ویدیو ارسال کنید ...')

    class Meta:
        unique_together = ('bot', 'lang')
        verbose_name = "Text"
        verbose_name_plural = "Texts"

    def __str__(self) -> str:
        return f'{self.bot} - {self.lang}'





class UserRefModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ref')
    ref = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refer')
    bot = models.ForeignKey(BotsModel, on_delete=models.CASCADE, related_name='user_references', null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'ref', 'bot')
        verbose_name = "User Referral"
        verbose_name_plural = "User Referrals"

    def __str__(self) -> str:
        return f'{self.user} -> {self.ref}'

    def clean(self):
        # Check if user is referring themselves
        if self.user == self.ref:
            raise ValidationError(_('A user cannot refer themselves.'))

        # Check if the ref user has already been referred by someone else
        if UserRefModel.objects.filter(ref=self.ref).exists():
            raise ValidationError(_('The user being referred has already been referred by someone else.'))

        # Check if the ref user is trying to refer back the user who referred them
        if UserRefModel.objects.filter(user=self.ref, ref=self.user).exists():
            raise ValidationError(_('The user being referred cannot refer back to the user who referred them.'))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)