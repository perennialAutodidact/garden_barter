from django.urls import path

from . import views

app_name="barters_app"

urlpatterns=[
    # path('', views.retreive, name='retrieve'),
    path('create/', views.create, name='create'),
]
