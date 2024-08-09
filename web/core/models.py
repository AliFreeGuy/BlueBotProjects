from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User




class LanguagesModel(models.Model):
    name = models.CharField(max_length=128, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"
    
    class Meta:
        verbose_name = "Language"
        verbose_name_plural = "Languages"



class ChannelsModel(models.Model):
    name = models.CharField(max_length=128)
    link = models.CharField(max_length=128 )
    chat_id = models.CharField(max_length=128  , null=True , blank=True)
    
    def __str__(self) -> str:
        return str(self.name)
    
    class Meta:
        verbose_name = "Channel"
        verbose_name_plural = "Channels"


class AdsModels(models.Model):
    
    name = models.CharField(max_length=256)
    url = models.CharField(max_length=256)

    def __str__(self) -> str:
        return f"{self.name} "
    
    class Meta:
        verbose_name = "Ads"
        verbose_name_plural = "Ads"


class BotsModel(models.Model):

    type = models.CharField(max_length=256 , default='none' , unique=True)
    username = models.CharField(max_length=256, unique=True)
    bot_token = models.CharField(max_length=256, unique=True)
    api_id = models.CharField(max_length=256)
    api_hash = models.CharField(max_length=256)
    session_string = models.TextField(null=True, blank=True, unique=True)

    def __str__(self) -> str:
        return self.username
    class Meta:
        verbose_name = "Bots"
        verbose_name_plural = "Bots"




class UserPaymentModel(models.Model):
    user  = models.ForeignKey(User , on_delete=models.CASCADE , related_name='payments')
    bot = models.ForeignKey(BotsModel , on_delete=models.CASCADE  , related_name='payments')
    status = models.BooleanField(default=False)
    amount = models.BigIntegerField()
    key = models.CharField(max_length=300)
    plan = models.IntegerField(default=0)
    creation = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{str(self.user)} - {str(self.amount)} - {str(self.status)}'
    
    class Meta:
                verbose_name = "Paymnet"
                verbose_name_plural = "Paymnet"





class SendMessage(models.Model):
    message = models.TextField()
    users = models.ManyToManyField(User, related_name='messages', blank=True)
    languages = models.ManyToManyField(LanguagesModel , related_name='messages' , blank=True)
    bots = models.ManyToManyField(BotsModel, related_name='messages')
    btns = models.ManyToManyField(AdsModels , related_name='messages' , blank=True)
    creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.message[:30]} ...'

    class Meta:
        verbose_name = "Send Message"
        verbose_name_plural = "Send Messages"






class BaseBotSettingModel(models.Model):
    bot = models.OneToOneField(BotsModel, related_name='setting', on_delete=models.CASCADE)
    zarin_key = models.CharField(max_length=256)
    bot_status = models.BooleanField(default=True)
    payment_status = models.BooleanField(default=False)
    admin_chat_id = models.CharField(max_length=256 )
    backup_channel = models.CharField(max_length=128)
    max_limit_payment = models.PositiveBigIntegerField(default=30000)
    channels = models.ManyToManyField(ChannelsModel, blank=True)
    ads = models.ManyToManyField(AdsModels, blank=True)
    langs = models.ManyToManyField(LanguagesModel, blank=True)
    
    class Meta:
        abstract = True



