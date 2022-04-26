from django.contrib import admin
from django.urls import path, include

from users_app import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('pages_app.views')),
    # path('login/', user_views.login, name='login'),
    # path('signup/', user_views.signup, name='signup'),
    path('',include('users_app.urls', namespace='users_app'))
    # path('logout/', user_views.logout),
]
