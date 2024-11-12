# attendance_system/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    check_in = models.DateTimeField(null=True, blank=True)  # 出勤時間
    check_out = models.DateTimeField(null=True, blank=True)  # 退勤時間
    date = models.DateField(default=timezone.now)  # 日付
    status = models.BooleanField(default=False)  # 勤務中か否か
    is_approved = models.BooleanField(default=False)  # 承認状態

    def __str__(self):
        check_in_str = self.check_in.strftime("%H:%M") if self.check_in else "未設定"
        check_out_str = self.check_out.strftime("%H:%M") if self.check_out else "未設定"
        approval_status = "承認済み" if self.is_approved else "再提出"
        return f"{self.user.username} - {self.date} (出勤: {check_in_str}, 退勤: {check_out_str}, 状態: {approval_status})"