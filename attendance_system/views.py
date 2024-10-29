# attendance_system/views.py
from django.shortcuts import render
from django.contrib.auth import login
from .forms import CustomUserCreationForm

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
