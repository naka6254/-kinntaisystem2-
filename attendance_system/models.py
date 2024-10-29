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

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    def calculate_working_hours(self):
        # 勤務時間の自動計算処理
        if self.check_out:
            return (self.check_out - self.check_in).total_seconds() / 3600
        return 0
