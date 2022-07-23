from django.dispatch import receiver
from django.db.models.signals import post_save
# from garden_barter_proj.settings import AUTH_USER_MODEL
from django.contrib.auth import get_user_model


@receiver(post_save, sender=get_user_model())
def create_inbox(sender, instance, **kwargs):
    from .models import Inbox

    Inbox.objects.get_or_create(user=instance)