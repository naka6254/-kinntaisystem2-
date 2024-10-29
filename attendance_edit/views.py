from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Attendance
from .forms import AttendanceForm
from user.models import User

@login_required
def register_attendance(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.user = request.user
            attendance.save()
            return redirect('attendance_list')
    else:
        form = AttendanceForm()
    return render(request, 'attendance_edit/register_attendance.html', {'form': form})

@login_required
def edit_attendance(request, attendance_id):
    attendance = get_object_or_404(Attendance, pk=attendance_id)
    if request.user.is_admin() or (request.user.is_manager() and attendance.user != request.user):
        if request.method == 'POST':
            form = AttendanceForm(request.POST, instance=attendance)
            if form.is_valid():
                form.save()
                return redirect('attendance_list')
        else:
            form = AttendanceForm(instance=attendance)
    return render(request, 'attendance_edit/edit_attendance.html', {'form': form, 'attendance': attendance})
