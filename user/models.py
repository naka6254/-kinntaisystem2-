from django.contrib.auth.models import AbstractUser
from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', '管理ユーザー'),
        ('manager', '上長ユーザー'),
        ('employee', '一般ユーザー'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def is_admin(self):
        return self.role == 'admin'

    def is_manager(self):
        return self.role == 'manager'

    def is_employee(self):
        return self.role == 'employee'
