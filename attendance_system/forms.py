# attendance_system/forms.py
from django import forms
from .models import Attendance
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError


class AttendanceEditForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['check_in', 'check_out', 'status']  # 編集可能なフィールド
        widgets = {
            'check_in': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'check_out': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(
        max_length=150,
        required=True,
        help_text=None,  # ヘルプテキストを非表示
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # username フィールドのバリデーションを削除
        self.fields['username'].validators = []

class CustomUserChangeForm(UserChangeForm):
    password1 = forms.CharField(
        label="新しいパスワード",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    password2 = forms.CharField(
        label="新しいパスワード（確認用）",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")
        
        if not username:
           self.add_error('username', "名前を入力してください。")

    
        if not email:
           self.add_error('email', "メールアドレスを入力してください。")

        if password1 and not password2:
            self.add_error('password2', "確認用パスワードを入力してください。")
        if password2 and not password1:
            self.add_error('password1', "パスワードを入力してください。")
        if password1 and password2 and password1 != password2:
            self.add_error('password2', "パスワードが一致しません。")
        if not password1 and not password2:
            raise forms.ValidationError("新しいパスワードを入力してください。")

        return cleaned_data



class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['check_in', 'check_out']
        widgets = {
            'check_in': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'check_out': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')

        # 出勤時間が退勤時間より後の場合
        if check_in and check_out:
            if check_in >= check_out:
                raise ValidationError("出勤時間は退勤時間よりも前である必要があります。")

            # 出勤日と退勤日が異なる日付の場合
            if check_in.date() != check_out.date():
                raise ValidationError("出勤日と退勤日は同じである必要があります。")

        return cleaned_data