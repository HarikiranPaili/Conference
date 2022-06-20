from .views import panelmember,panelmember_action,panelmember_edit
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [

    path('panelmember', panelmember, name='panelmember'),
    path('panelmember_edit/<int:id>/', panelmember_edit, name='panelmember_edit'),
    path('panelmember_action', panelmember_action, name='panelmember_action'),
]