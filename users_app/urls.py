from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)

from . import views

app_name = 'users_app'

urlpatterns = [
    path('register/', views.register, name='register'),  # create user
    path('user/', views.get_user, name='get_user'), # get logged in user
    path('user/update/', views.update, name='update'),
    # path('login/', views.login, name='login'), # login user
    # path('token/', views.extend_token, name='extend_token'), # request new access tokens
    # path('detail/<int:pk>/', views.user_detail, name='detail'),  # read/update
    # path('logout/', views.logout, name='logout'), # delete tokens,

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
]
