from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    prn_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)  # ← add this

    def __str__(self):
        return f"{self.name} - {self.prn_number}"

class Faculty(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('busy', 'Busy in Lecture'),
        ('meeting', 'In Meeting'),
        ('not_available', 'Not Available'),
    )
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"{self.name} - {self.status}"
    def is_within_working_hours(self):
        from django.utils import timezone
        now = timezone.localtime()
        day_map = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'}
        today = day_map.get(now.weekday())
        current_time = now.time()

        schedules_today = self.schedules.filter(day=today)
        for schedule in schedules_today:
            if schedule.start_time <= current_time <= schedule.end_time:
                return True
        return False

    def todays_schedule(self):
        from django.utils import timezone
        now = timezone.localtime()
        day_map = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'}
        today = day_map.get(now.weekday())
        return self.schedules.filter(day=today).first()   
class Schedule(models.Model):
    DAY_CHOICES = (
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
    )
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='schedules')
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['day', 'start_time']

    def __str__(self):
        return f"{self.faculty.name} - {self.get_day_display()} {self.start_time}-{self.end_time}"