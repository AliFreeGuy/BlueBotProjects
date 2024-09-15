from django.db import models
from core.models import BaseBotSettingModel , ChannelsModel
from accounts.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from core.models import BotsModel , LanguagesModel
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _




class CompressorSettingModel(BaseBotSettingModel):
    max_limit_video = models.PositiveBigIntegerField()
    max_limit_free_video = models.PositiveBigIntegerField(default=100)
    quality_1 =  models.IntegerField(default=1)
    quality_2 =  models.IntegerField(default=1)
    quality_3 = models.IntegerField(default=1)
    watermark_text = models.CharField(null=True , blank=True , max_length=128)
    watermark_color = models.CharField(max_length=128 , null=True , blank=True )
    watermark_size = models.PositiveIntegerField(null=True , blank=True)

    ref_volume = models.PositiveBigIntegerField(default=0)
    join_volume = models.PositiveBigIntegerField(default=0)
    add_volume_channels = models.ManyToManyField(ChannelsModel, blank=True  , related_name='compressor_setting')
    






    WATERMARK_POSITIONS = [
        ('top_left', 'گوشه بالا سمت چپ'),
        ('top_right', 'گوشه بالا سمت راست'),
        ('bottom_left', 'گوشه پایین سمت چپ'),
        ('bottom_right', 'گوشه پایین سمت راست'),
        ('center', 'مرکز'),
    ]
    watermark_position = models.CharField(
        max_length=20,
        choices=WATERMARK_POSITIONS,
        default='bottom_right',
        verbose_name="watermark positions"
    )
    class Meta:
        verbose_name = "Setting"
        verbose_name_plural = "Settings"




class CompressorPlansModel(models.Model):
    bot = models.ForeignKey(BotsModel , related_name='plans' , on_delete=models.CASCADE)
    tag = models.SlugField(max_length=128, unique=True, default='compressor')
    name = models.CharField(max_length=128, unique=True)
    name_en = models.CharField(max_length=128, unique=True , null=True , blank=True)
    description = models.TextField()
    description_en = models.TextField(null=True , blank=True)
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
            existing_instance = CompressorUser.objects.get(pk=self.pk)

            if existing_instance.plan != self.plan:
                if self.plan:
                    self.volume = self.plan.volume
                    self.expiry = timezone.now() + timezone.timedelta(days=self.plan.day)
                else:
                    self.volume = 0
                    self.expiry = None

            if self.expiry and self.expiry < timezone.now():
                self.plan = None
                self.volume = 0
                self.expiry = None
                self.is_active = False
        else:
            if not self.plan:
                try:
                    free_plan = CompressorPlansModel.objects.get(tag='free')
                    self.plan = free_plan
                    self.volume = free_plan.volume
                    self.expiry = timezone.now() + timezone.timedelta(days=free_plan.day)
                    self.is_active = True
                except CompressorPlansModel.DoesNotExist:
                    pass

            if not self.bot:
                try:
                    compressor_bot = BotsModel.objects.get(type='compressor')
                    self.bot = compressor_bot
                except BotsModel.DoesNotExist:
                    pass

        # Check if lang is not set, assign 'fa' language
        if not self.lang:
            try:
                fa_lang = LanguagesModel.objects.get(code='fa')
                self.lang = fa_lang
            except LanguagesModel.DoesNotExist:
                pass

        if not self.plan:
            self.volume = 0
            self.expiry = None
            self.is_active = False

            try:
                free_plan = CompressorPlansModel.objects.get(tag='free')
                self.plan = free_plan
                self.volume = free_plan.volume
                self.expiry = timezone.now() + timezone.timedelta(days=free_plan.day)
                self.is_active = True
            except CompressorPlansModel.DoesNotExist:
                pass

        if not self.quality:
            self.quality = 'quality_2'

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
    placeholder_text = models.CharField(max_length=128 , default='ویدیو ارسال کنید ...')
    editor_progress_text = models.TextField(default='متن هنگام ادیت ویدیو ....')
    plans_text = models.TextField(default='متن اشتراک ها')
    max_limit_text = models.TextField(default='متن حجم مجاز')
    user_sub_change_text = models.TextField(default='متن وقتی که اشتراک کاربر تغییر میکنه')
    profile_btn = models.CharField(max_length=25 , default='پروفایل')
    setting_btn = models.CharField(max_length=25 , default='تنظیمات')
    help_btn = models.CharField(max_length=25 , default='راهنما')
    support_btn  = models.CharField(max_length=25 , default='پشتیبانی')
    plans_btn = models.CharField(max_length=25 , default='اشتراک')
    i_joined_btn_text = models.CharField(max_length=128 , default='عضو شدم')
    add_volume_with_ref_text_share = models.TextField(default='متن اشتراک گذاری لینک دعوت کاربران')
    add_volume_with_ref_btn = models.CharField(max_length=128 , default='افزایش حجم با زیرمجموعه گیری')
    add_volume_with_join_btn = models.CharField(max_length=128 , default='افزایش حجم با عضویت در کانال')
    add_volume_with_payment_btn = models.CharField(max_length=128 , default='افزایش حجم با خرید اشتراک')
    sign_text = models.TextField(default  = 'متن امضا زیر پیام ادیتور')

    add_volume_with_join_text = models.TextField(default='متن افزایش حجم با جوین')
    add_volume_with_ref_text = models.TextField(default='متن افزایش حجم با زیرمجموعه')
    user_ref_text = models.TextField(default='متن وقتی که کاربر زیر مجموعه میگیره و ارسال میشه بهش میگه این کاربر وارد ربات شد' )
    user_join_text = models.TextField(default='متن وقتی کاربر عضو کانال ها برای افزایش حجم میشه ' ,)


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