from django.urls import path

from . import views

app_name="messages_app"

urlpatterns=[
    path('', views.inbox, name='inbox'),
    path('messages/create/', views.create, name="create"),
    # path('messages/<int:message_id>/', views.inbox, name='message_detail'),
    path('conversations/find/', views.find_conversation, name="find_conversation"),
    path('conversations/<int:conversation_id>/', views.conversations, name='conversations')
]