from .views import reviewer,reviewer_action,email
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [

    path('reviewer', reviewer, name='reviewer'),
    path('email/<int:id>/', email, name='email'),
    path('reviewer_action', reviewer_action, name='reviewer_action'),


]