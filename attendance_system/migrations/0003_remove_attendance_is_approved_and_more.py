# Generated by Django 5.1.2 on 2024-11-16 01:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_system', '0002_attendance_is_approved'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='is_approved',
        ),
        migrations.AlterField(
            model_name='attendance',
            name='status',
            field=models.CharField(choices=[('pending', '申請中'), ('approved', '承認済み'), ('resubmitted', '再提出')], default='pending', max_length=20),
        ),
    ]