from django.contrib import admin

from .models import Inbox, Conversation, Message

admin.site.register([Inbox, Conversation, Message])
