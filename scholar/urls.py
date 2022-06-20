from .views import index, dashboard, logout_view, add_proposal, failed, webhook, copy_leaks, login_view, close, \
    login_auth, get_res, admin, get_title,scholar_edited,superv_approval,superv_reject
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', index, name='index'),
    path('sa', admin, name='admin'),
    path('scholar_edited', scholar_edited, name='scholar_edited'),
    path('close', close, name='close'),
    path('login', login_view, name='login'),
    path('login_auth', login_auth, name='login_auth'),
    path('failed', failed, name='failed'),
    path('get_res', get_res, name='get_res'),
    path('get_title', get_title, name='get_title'),
    path('logout', logout_view, name='logout_view'),
    path('dashboard', dashboard, name='dashboard'),
    path('add_proposal', add_proposal, name='add_proposal'),
    path('copy_leaks', copy_leaks, name='copy_leaks'),
    path('webhook/<str:status>/<int:scanid>/', webhook, name='webhook'),
    path('superv_approval/<str:pk>',superv_approval,name='superv_approval'),
    path('superv_reject/<str:pk>', superv_reject, name='superv_reject')

]
