from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from common.utils import get_uuid_hex

class Inbox(models.Model):
    user = models.OneToOneField(get_user_model(), verbose_name=_(
        'user'), on_delete=models.CASCADE, related_name='inbox')

    class Meta:
        verbose_name_plural = 'inboxes'

    def __str__(self):
        return f"Inbox - {self.user.email}"

class Conversation(models.Model):
    uuid = models.CharField(_('uuid'), max_length=32, default=get_uuid_hex)
    inbox = models.ForeignKey(Inbox, on_delete=models.CASCADE, related_name='conversations')
    barter_id = models.PositiveIntegerField(verbose_name=_('barter id'))
    barter_type = models.CharField(_('barter type'), max_length=10)
    sender = models.ForeignKey(get_user_model(),
        on_delete=models.CASCADE, verbose_name=_('sender'), related_name="coversations")
    recipient = models.ForeignKey(get_user_model(),
        on_delete=models.CASCADE, verbose_name=_('recipient'), related_name="conversations")

class Message(models.Model):

    uuid = models.CharField(_('uuid'), max_length=32, default=get_uuid_hex)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, verbose_name=_(
        'conversation'), related_name='messages')
    sender = models.ForeignKey(get_user_model(), 
        on_delete=models.CASCADE, verbose_name=_('sender'), related_name="messages_sent")
    recipient = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_(
        'recipient'),  related_name="messages_received")
    date_received = models.DateTimeField(_('date received'), auto_now_add=True)
    body = models.TextField(_('body'), max_length=1000)
