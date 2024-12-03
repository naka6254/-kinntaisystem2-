from django.shortcuts import redirect
from django.conf import settings
from django.urls import resolve

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ログイン不要なURL（'welcome'と'login'）
        excluded_urls = ['welcome', 'login']
        current_url_name = resolve(request.path_info).url_name

        # 未ログインかつ保護されたURLにアクセスした場合、リダイレクト
        if not request.user.is_authenticated and current_url_name not in excluded_urls:
            return redirect(settings.LOGIN_URL)

        return self.get_response(request)
