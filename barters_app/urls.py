from django.urls import path

from . import views

app_name="barters_app"

urlpatterns=[
    path('create/', views.create, name='create'),
    path('', views.retrieve, name='retrieve'), # retrieve all barters of all types
    path('<str:barter_type>/', views.retrieve, name='retrieve'), # retrieve all barters of a single type
    path('<str:barter_type>/<int:barter_id>/', views.retrieve, name='retrieve'), # retrieve a single barter of a single type
]
