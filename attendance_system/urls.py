"""
URL configuration for attendance_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views 
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.welcome, name='welcome'),
    path('login/', auth_views.LoginView.as_view(template_name='attendance_system/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), 
    path('register/', views.register, name='register'), 
    path('attendance/', views.attendance_view, name='attendance'),
    path('update_profile/', views.update_profile, name='update_profile'), 
    path('attendance/edit/<int:attendance_id>/', views.edit_attendance, name='edit_attendance'), 
    path('attendance/approve/<int:attendance_id>/', views.approve_attendance, name='approve_attendance'),
    path('attendance/approval/', views.attendance_approval, name='attendance_approval'),
    path('attendance/edit/<int:id>/', views.edit_attendance, name='edit_attendance'),
    path('attendance/update/<int:id>/', views.update_attendance, name='update_attendance'),
]
