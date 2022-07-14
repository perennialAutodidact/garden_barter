from django.db import models
from django.contrib.auth import get_user_model


class Inbox(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='user')

class Message(models.Model):
    inbox = models.ForeignKey(Inbox, on_delete=models.CASCADE, related_name='messages')
    sender  = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="messages")
    recipient = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="messages")
    date_received = models.DateTimeField(auto_now_add=True)