# attendance_system/views.py
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Attendance

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 登録後に自動ログイン
            return redirect('welcome')  # 登録成功後にウェルカムページへリダイレクト
    else:
        form = CustomUserCreationForm()
    return render(request, 'attendance_system/register.html', {'form': form})

def welcome(request):
    return render(request, 'attendance_system/welcome.html')

@login_required
def attendance_view(request):
    user = request.user
    today = timezone.now().date()

    # 今日の出勤データを取得
    attendance, created = Attendance.objects.get_or_create(user=user, date=today)

    if request.method == 'POST':
        if 'check_in' in request.POST and not attendance.check_in:
            attendance.check_in = timezone.now()
            attendance.status = True  # 出勤中に設定
            attendance.save()
        elif 'check_out' in request.POST and attendance.check_in and not attendance.check_out:
            attendance.check_out = timezone.now()
            attendance.status = False  # 勤務終了に設定
            attendance.save()
        return redirect('attendance')

    return render(request, 'attendance_system/attendance.html', {'attendance': attendance})
