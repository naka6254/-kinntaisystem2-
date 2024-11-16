from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('unupdated', '未更新'),
        ('pending', '申請中'),
        ('approved', '承認済み'),
        ('rejected', '再提出'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ユーザーとのリレーション
    check_in = models.DateTimeField(null=True, blank=True)  # 出勤時間
    check_out = models.DateTimeField(null=True, blank=True)  # 退勤時間
    date = models.DateField(default=now)  # 日付
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='unupdated'  # デフォルトは未更新
    )
    is_approved = models.BooleanField(default=None, null=True, blank=True)  # 承認状態

    def update_status(self):
        """状態を自動更新"""
        if self.is_approved is None:  # 承認も再提出もされていない
            self.status = 'pending'
        elif self.is_approved:
            self.status = 'approved'
        else:
            self.status = 'rejected'
        self.save()

    def approve(self):
        """承認処理"""
        self.is_approved = True
        self.update_status()

    def reject(self):
        """再提出処理"""
        self.is_approved = False
        self.update_status()

    @property
    def status_display(self):
        """状態のラベルを取得"""
        return dict(self.STATUS_CHOICES).get(self.status, "未設定")

    def __str__(self):
        """オブジェクトの文字列表現"""
        check_in_str = self.check_in.strftime("%H:%M") if self.check_in else "未設定"
        check_out_str = self.check_out.strftime("%H:%M") if self.check_out else "未設定"
        return f"{self.user.username} - {self.date} (出勤: {check_in_str}, 退勤: {check_out_str}, 状態: {self.status_display})"
