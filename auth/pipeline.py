from django.http import HttpResponseRedirect
from usermanagement.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login
def get_user(backend, user, response, *args, **kwargs):
    if backend.name == 'google-oauth2':
        # print(user.social_auth.filter(provider='google-oauth2',uid=kwargs['uid']))
        if kwargs:
            email = kwargs['uid']
            S = User.objects.filter(email=email).values().distinct()
            if S:
                S.update(flag_counter=True)
                print(user)
                return user
            else:
                return HttpResponseRedirect('/failed')
