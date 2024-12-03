# attendance_system/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomUserChangeForm, AttendanceEditForm
from .models import Attendance
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import AttendanceForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import redirect
import logging

logger = logging.getLogger(__name__)

@login_required
def debug_view(request):
    return JsonResponse({"is_authenticated": request.user.is_authenticated})


def login_view(request):
    next_url = request.GET.get('next', '/attendance/')  # next_urlが指定されていない場合、'/attendance/' にリダイレクト

    form = AuthenticationForm(request, data=request.POST or None)  # フォームインスタンスを作成
    if request.method == 'POST':
        if form.is_valid():  # フォームの検証
            user = form.get_user()  # フォームから認証されたユーザーを取得
            login(request, user)  # ユーザーをログイン
            return redirect(next_url)  # next_url（もしくはデフォルトでattendanceページ）にリダイレクト
        else:
            messages.error(request, 'ユーザー名またはパスワードが正しくありません。')  # 認証エラー
    return render(request, 'attendance_system/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    if request.user.is_authenticated:
        logger.info(f"User {request.user.username} logged out")
    logout(request)
    request.session.flush()
    return redirect('/')



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
def edit_attendance_manager(request, id):
    attendance = get_object_or_404(Attendance, id=id)
    # 編集処理を記述
    return render(request, 'edit_attendance_manager.html', {'attendance': attendance})


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
@login_required
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

    return render(request, 'update_attendance.html', {'form': form, 'attendance': attendance})

@login_required    
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
    attendances = Attendance.objects.exclude(user__groups__name='幹部クラス')

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
        elif action == "delete":
            attendance.delete()
            messages.success(request, "出退勤情報が削除されました。")

    return render(request, "attendance_system/attendance_approval.html", {"attendances": attendances})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='幹部クラス').exists())
def change_user_permissions(request, user_id):
    user = get_object_or_404(User, id=user_id)  # 指定された ID のユーザーを取得
    groups = Group.objects.all()  # 全グループを取得

    if request.method == 'POST':
        selected_group_ids = request.POST.getlist('groups')  # 選択されたグループIDを取得
        selected_groups = Group.objects.filter(id__in=selected_group_ids)  # 対象グループを取得

        # 現在のグループをクリアして新しいグループを設定
        user.groups.clear()
        user.groups.add(*selected_groups)

        messages.success(request, f"{user.username} の権限を変更しました。")
        return redirect('user_management')  # 権限変更後にユーザー管理画面へリダイレクト

    return render(request, 'attendance_system/change_permissions.html', {
        'user': user,
        'groups': groups,
    })



@login_required
@user_passes_test(lambda u: u.groups.filter(name='幹部クラス').exists())
def change_user_permissions(request, user_id):
    user = get_object_or_404(User, id=user_id)
    groups = Group.objects.all()  # すべての役職を取得

    if request.method == 'POST':
        selected_group_id = request.POST.get('group')  # フォームデータから役職IDを取得

        if selected_group_id:  # 選択された役職が存在する場合
            selected_group = get_object_or_404(Group, id=selected_group_id)
            user.groups.clear()  # 現在の役職をクリア
            user.groups.add(selected_group)  # 新しい役職を設定
            messages.success(request, f"{user.username} の役職を {selected_group.name} に変更しました。")
        else:
            messages.error(request, "役職を選択してください。")

        return redirect('change_user_permissions', user_id=user.id)

    return render(request, 'attendance_system/change_permissions.html', {
        'user': user,
        'groups': groups,
        'all_users': User.objects.all(),  # 全社員リスト
    })


@login_required
def delete_user_view(request, user_id=None):
    if user_id:  # 指定されたユーザーIDがある場合
        user = get_object_or_404(User, id=user_id)  # 該当ユーザーを取得
        if request.method == "POST":  # POSTリクエストで削除を実行
            username = user.username
            user.delete()
            messages.success(request, f"ユーザー {username} が削除されました。")
            return redirect('delete_user_view')  # ユーザー一覧にリダイレクト

    # 全ユーザーを取得してテンプレートに渡す
    all_users = User.objects.all().order_by('username')
    context = {
        'all_users': all_users
    }
    return render(request, 'delete_user.html', context)