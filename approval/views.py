from django.shortcuts import get_object_or_404, redirect
from .models import Attendance
from django.contrib.auth.decorators import login_required
from user.models import User

@login_required
def approve_attendance(request, attendance_id):
    attendance = get_object_or_404(Attendance, pk=attendance_id)
    if request.user.is_admin():
        attendance.status = 'approved'
        attendance.save()
    return redirect('attendance_list')

@login_required
def resubmit_attendance(request, attendance_id):
    attendance = get_object_or_404(Attendance, pk=attendance_id)
    if request.user.is_admin():
        attendance.status = 'resubmitted'
        attendance.save()
    return redirect('attendance_list')
