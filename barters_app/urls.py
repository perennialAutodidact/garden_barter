from django.urls import path

from . import views

app_name="barters_app"

urlpatterns=[
    path('create/', views.create, name='create'),
    path('update/<str:barter_type>/<str:barter_id>/', views.update, name='update'), # retrieve a single barter of a single type
    path('', views.retrieve, name='retrieve'), # retrieve all barters of all types
    path('<str:barter_type>/', views.retrieve, name='retrieve'), # retrieve all barters of a single type
    path('<str:barter_type>/<str:barter_id>/', views.retrieve, name='retrieve'), # retrieve a single barter of a single type
]
