from django.shortcuts import render

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm

from .forms import UserLoginForm, UserSignupForm

from django.template.defaulttags import register

@register.filter
def get_range(value):
    return range(value)

def login(request):
    if request.method == 'GET':

        context = {
            'form': UserLoginForm(),
            'form_mode': 'log in'
        }

        return render(request, 'users/auth.html', context)


def signup(request):
    if request.method == 'GET':

        context = {
            'form': UserSignupForm(),
            'form_mode': 'sign up'
        }

        return render(request, 'users/auth.html', context)
