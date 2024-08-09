from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SendMessage
from core.tasks import message_sender



@receiver(post_save, sender=SendMessage)
def print_send_message(sender, instance, created, **kwargs):
    if created:
        print('###################################################')
        message_sender.delay_on_commit(instance.id)
        print(f"New SendMessage saved: {instance.message} - Created at: {instance.creation}")
        print('###################################################')
 