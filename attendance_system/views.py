# attendance_system/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import CustomUserCreationForm, CustomUserChangeForm, AttendanceEditForm
from .models import Attendance
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import AttendanceForm



def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "ユーザー登録が完了しました。ログインしてください。")
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
            user = form.save(commit=False)  # 一旦保存を遅延
            if form.cleaned_data.get('password1'):
                user.set_password(form.cleaned_data['password1'])  # パスワードをハッシュ化
            user.save()
            login(request, user)  # パスワード変更後に再ログイン
            messages.success(request, "プロフィールが正常に更新されました！")
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

    # 中間管理職が閲覧できるデータを制限 (幹部クラスを除く)
    manager_viewable_users = User.objects.exclude(groups__name='幹部クラス')
    attendances = Attendance.objects.filter(user__in=manager_viewable_users)

    # 中間管理職のみがアクセス可能
    if user.groups.filter(name='中間管理職').exists():
        # 編集対象ユーザーが幹部クラスに属していないかを確認
        if not attendance.user.groups.filter(name='幹部クラス').exists():
            if request.method == 'POST':
                form = AttendanceEditForm(request.POST, instance=attendance)
                if form.is_valid():
                    form.save()
                    messages.success(request, "出退勤データが更新されました。")
                    return redirect('attendance_approval')  # 編集後に管理画面にリダイレクト
            else:
                form = AttendanceEditForm(instance=attendance)

            # 中間管理職用テンプレートにフォームと制限された出退勤データを渡す
            return render(request, 'attendance_system/edit_attendance_manager.html', {
                'form': form,
                'attendance': attendance,
                'attendances': attendances,  # フィルタリングされた出退勤データ
            })

        else:
            # 幹部クラスの出退勤情報にはアクセスできない
            messages.error(request, "幹部クラスの出退勤データは編集できません。")
            return redirect('attendance_approval')

    # 中間管理職以外のユーザーはアクセス不可
    else:
        messages.error(request, "編集権限がありません。")
        return redirect('attendance_approval')

def update_attendance(request, id):
    attendance = get_object_or_404(Attendance, id=id)

    if request.method == "POST":
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            messages.success(request, "更新されました！")
            return redirect(f'/attendance/edit/{id}/') 
    else:
        form = AttendanceForm(instance=attendance)

    return render(request, 'update_attendance.html', {'form': form})  
    
def approve_attendance(request, attendance_id):  
    
    attendance = get_object_or_404(Attendance, id=attendance_id)

    if request.method == 'POST':
        if 'approve' in request.POST:
            attendance.is_approved = True  # 承認済みに設定
            attendance.save()
        elif 'resubmit' in request.POST:
            attendance.is_approved = False  # 再提出に設定
            attendance.save()
            
    return redirect('attendance')


@login_required
@user_passes_test(lambda u: u.groups.filter(name='幹部クラス').exists())
def attendance_approval(request):
    # Attendanceモデルから全社員の出退勤データを取得
    attendances = Attendance.objects.all()
    return render(request, 'attendance_system/edit_attendance_admin.html', {'attendances': attendances})


@login_required
def attendance_approval(request):
    attendances = Attendance.objects.all()

    if request.method == "POST":
        attendance_id = request.POST.get("attendance_id")
        action = request.POST.get("action")
        attendance = get_object_or_404(Attendance, id=attendance_id)

        if action == "approve":
            attendance.approve()
            messages.success(request, f"{attendance.user.username} さんの出退勤が承認されました。")
        elif action == "resubmit":
            attendance.reject()
            messages.warning(request, f"{attendance.user.username} さんの出退勤が再提出されました。")

    return render(request, "attendance_system/attendance_approval.html", {"attendances": attendances})