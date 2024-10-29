from django.db import models
from user.models import User

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=(
        ('submitted', '提出済み'),
        ('approved', '承認済み'),
        ('resubmitted', '再提出'),
    ), default='submitted')

    def calculate_work_hours(self):
        if self.start_time and self.end_time:
            start_dt = datetime.combine(self.date, self.start_time)
            end_dt = datetime.combine(self.date, self.end_time)
            work_duration = end_dt - start_dt
            return work_duration.total_seconds() / 3600
        return 0
