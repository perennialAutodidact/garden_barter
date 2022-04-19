from django.urls import path

from . import views

app_name='users_app'

urlpatterns = [
    path('register/', views.register, name='register'), # create user
    path('auth/', views.auth, name='auth'), # get logged in user
    path('login/', views.login, name='login'), # login user
    path('token/', views.extend_token, name='extend_token'), # request new access tokens
    path('detail/<int:pk>/', views.user_detail, name='detail'), # read/update
    path('logout/', views.logout, name='logout'), # delete tokens
]
