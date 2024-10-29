from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_attendance, name='register_attendance'),
    path('edit/<int:attendance_id>/', views.edit_attendance, name='edit_attendance'),
]
