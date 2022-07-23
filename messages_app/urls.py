from django.urls import path

from . import views

app_name="messages_app"

urlpatterns=[
    path('create/', views.create, name="create"),
    path('inbox/', views.inbox, name='inbox'),
    # path('inbox/messages/<int:message_id>/', views.inbox, name='message_detail'),
    path('inbox/conversations/<int:conversation_id>/', views.conversations, name='conversations')
]