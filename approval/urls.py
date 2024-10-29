from django.urls import path
from . import views

urlpatterns = [
    path('approve/<int:attendance_id>/', views.approve_attendance, name='approve_attendance'),
    path('resubmit/<int:attendance_id>/', views.resubmit_attendance, name='resubmit_attendance'),
]
