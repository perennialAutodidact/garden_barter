from django.contrib import messages
from django.contrib.auth import authenticate, django_logout
from django.contrib.auth import login as django_login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.template.defaulttags import register
from django.urls import reverse

from .forms import UserLoginForm, UserSignupForm


@register.filter
def get_range(value):
    '''returns a range from 0 to value, not including value'''
    return range(value)


def login(request):
    if request.method == 'GET':

        context = {
            'form': UserLoginForm(),
            'form_mode': 'log in'
        }

        return render(request, 'users/auth.html', context)

    elif request.method == 'POST':
        form = UserLoginForm(request.POST)

        if form.is_valid():
            pass

        else:
            context = {
                'form': form,
                'form_mode': 'log in'
            }
        return render(request, 'users/auth.html', context)


def signup(request):

    context = {
        'form_mode': 'sign up'
    }

    if request.method == 'GET':

        context.update({
            'form': UserSignupForm(),
        })

        return render(request, 'users/auth.html', context)

    elif request.method == 'POST':
        form = UserSignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            django_login(request, user)
            return redirect(reverse("pages_app:home"))

        else:
            context.update({
                'form': form,
            })
        return render(request, 'users/auth.html', context)
