# attendance_system/models.py
from django.db import models
from django.contrib.auth.models import User

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    # その他必要なフィールド

    def calculate_working_hours(self):
        # 勤務時間の自動計算処理
        if self.check_out:
            return (self.check_out - self.check_in).total_seconds() / 3600
        return 0
