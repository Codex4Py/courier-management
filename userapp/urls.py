from django.contrib import admin
from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
    path('dashboard-2/', views.dashboard_2, name='dashboard_2'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('update_profile/', views.UserUpdateView.as_view(), name='UserUpdateView'),
]
