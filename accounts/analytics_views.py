from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncDate
from queue_app.models import QueueToken, Request
from accounts.models import Faculty, Student
import json


@login_required
def analytics_dashboard(request):
    # Only admin can access
    if request.user.role != 'admin':
        from django.shortcuts import redirect
        return redirect('dashboard')

    # 1. Total students served per day (last 7 days)
    daily_stats = QueueToken.objects.filter(
        status='completed'
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')[:7]

    daily_labels = [str(item['date']) for item in daily_stats]
    daily_data = [item['count'] for item in daily_stats]

    # 2. Request type breakdown (pie chart)
    request_types = QueueToken.objects.values(
        'request_type'
    ).annotate(
        count=Count('id')
    ).order_by('-count')

    request_labels = [item['request_type'] for item in request_types]
    request_data = [item['count'] for item in request_types]

    # 3. Busiest faculty (bar chart)
    busy_faculty = QueueToken.objects.values(
        'faculty__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    faculty_labels = [item['faculty__name'] for item in busy_faculty]
    faculty_data = [item['count'] for item in busy_faculty]

    # 4. Summary stats
    total_served = QueueToken.objects.filter(status='completed').count()
    total_waiting = QueueToken.objects.filter(status='waiting').count()
    total_students = Student.objects.count()
    total_faculty = Faculty.objects.count()

    return render(request, 'accounts/analytics.html', {
        'daily_labels': json.dumps(daily_labels),
        'daily_data': json.dumps(daily_data),
        'request_labels': json.dumps(request_labels),
        'request_data': json.dumps(request_data),
        'faculty_labels': json.dumps(faculty_labels),
        'faculty_data': json.dumps(faculty_data),
        'total_served': total_served,
        'total_waiting': total_waiting,
        'total_students': total_students,
        'total_faculty': total_faculty,
    })