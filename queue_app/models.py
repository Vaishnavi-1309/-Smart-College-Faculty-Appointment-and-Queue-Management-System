from django.db import models
from accounts.models import Student, Faculty

class Request(models.Model):
    REQUEST_TYPE_CHOICES = (
        ('signature', 'Signature'),
        ('assignment', 'Assignment Submission'),
        ('doubt', 'Doubt Solving'),
        ('project', 'Project Discussion'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class QueueToken(models.Model):
    STATUS_CHOICES = (
        ('waiting', 'Waiting'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    token_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    request_type = models.CharField(max_length=20, default='signature')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['token_number']