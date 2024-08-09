from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, chat_id, full_name, password=None):
        if not chat_id:
            raise ValueError('User must have a chat_id')
        if not full_name:
            raise ValueError('User must have full_name')
      
        user = self.model(chat_id=chat_id, full_name=full_name, is_active=True)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, chat_id, full_name, password):
        user = self.create_user(chat_id, full_name, password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
