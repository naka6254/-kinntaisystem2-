# attendance_system/views.py
from django.shortcuts import render

def welcome(request):
    return render(request, 'attendance_system/welcome.html')
