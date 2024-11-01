# attendance_system/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import CustomUserCreationForm, CustomUserChangeForm, AttendanceEditForm
from .models import Attendance
from django.contrib.auth.decorators import login_required, user_passes_test


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

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('attendance')  # 出勤管理画面にリダイレクト
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'attendance_system/update_profile.html', {'form': form})

def welcome(request):
    return render(request, 'attendance_system/welcome.html')

@login_required
def attendance_view(request):
    user = request.user
    today = timezone.now().date()

    # 今日の出勤データを取得（または作成）
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

    # 役職情報をテンプレートに渡す
    is_admin = user.groups.filter(name='幹部クラス').exists()
    is_manager = user.groups.filter(name='中間管理職').exists()
    is_employee = user.groups.filter(name='一般社員').exists()

    return render(request, 'attendance_system/attendance.html', {
        'attendance': attendance,
        'is_admin': is_admin,
        'is_manager': is_manager,
        'is_employee': is_employee,
    })

@login_required
def edit_attendance(request, attendance_id):
    user = request.user
    attendance = get_object_or_404(Attendance, id=attendance_id)

    # 幹部クラス（管理ユーザー）の場合
    if user.groups.filter(name='幹部クラス').exists():
        if request.method == 'POST':
            if 'approve' in request.POST:
                attendance.is_approved = True
                attendance.save()
            elif 'resubmit' in request.POST:
                attendance.is_approved = False
                attendance.save()
            return redirect('attendance')  # 承認または再提出後のリダイレクト
        return render(request, 'attendance_system/edit_attendance_admin.html', {'attendance': attendance})

    # 中間管理職の場合
    elif user.groups.filter(name='中間管理職').exists():
        if request.method == 'POST':
            form = AttendanceEditForm(request.POST, instance=attendance)
            if form.is_valid():
                form.save()
                return redirect('attendance')
        else:
            form = AttendanceEditForm(instance=attendance)
        return render(request, 'attendance_system/edit_attendance_manager.html', {'form': form, 'attendance': attendance})

    # 一般社員の場合
    elif user.groups.filter(name='一般社員').exists():
        if request.method == 'POST':
            form = AttendanceEditForm(request.POST, instance=attendance)
            if form.is_valid():
                form.save()
                return redirect('attendance')
        else:
            form = AttendanceEditForm(instance=attendance)
        return render(request, 'attendance_system/edit_attendance_employee.html', {'form': form, 'attendance': attendance})

    # 該当グループに所属しないユーザーはアクセス禁止
    else:
        return redirect('attendance')
    
def approve_attendance(request, attendance_id):  
    
    attendance = get_object_or_404(Attendance, id=attendance_id)

    if request.method == 'POST':
        if 'approve' in request.POST:
            attendance.status = '承認済み'
            attendance.save()
        elif 'resubmit' in request.POST:
            attendance.status = '再提出'
            attendance.save()

    return redirect('attendance')


@login_required
@user_passes_test(lambda u: u.groups.filter(name='幹部クラス').exists())
def attendance_approval(request):
    # Attendanceモデルから全社員の出退勤データを取得
    attendances = Attendance.objects.all()
    return render(request, 'attendance_system/edit_attendance_admin.html', {'attendances': attendances})
