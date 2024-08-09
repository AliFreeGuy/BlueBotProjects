from django.db import models
from django.contrib.auth.models import AbstractBaseUser , PermissionsMixin
from .managers import UserManager


class User(AbstractBaseUser , PermissionsMixin):
    
    chat_id = models.BigIntegerField(unique=True)
    full_name = models.CharField(max_length=128 , null=True ,blank=True)
    wallet = models.PositiveBigIntegerField(default=0)
    phone = models.CharField(max_length=12 , default='none')
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    creation = models.DateTimeField(auto_now_add=True)

    
    USERNAME_FIELD = 'chat_id'
    REQUIRED_FIELDS = ['full_name' , ]

    objects = UserManager()


    def __str__(self) -> str:
        return f'{str(self.chat_id)} - {self.full_name}'
    

    @property
    def is_staff(self):
        return self.is_admin
    
    class Meta :

        verbose_name = "All Users"
        verbose_name_plural = "All Users"


