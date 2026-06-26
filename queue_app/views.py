from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import Faculty
from queue_app.models import QueueToken, Request


@login_required
def join_queue(request):
    faculty_id = request.GET.get('faculty_id')
    selected_faculty = None
    if faculty_id:
        selected_faculty = get_object_or_404(Faculty, id=faculty_id)

    if request.method == 'POST':
        faculty_id = request.POST.get('faculty_id')
        request_type = request.POST.get('request_type')
        faculty = get_object_or_404(Faculty, id=faculty_id)
        student = request.user.student

        # Check if student already in this queue
        already_in = QueueToken.objects.filter(
            student=student,
            faculty=faculty
        ).exclude(status='completed').exists()

        if already_in:
            messages.warning(request, 'You are already in this queue!')
            return redirect('student_dashboard')

        # Generate next token number for this faculty
        last_token = QueueToken.objects.filter(
            faculty=faculty
        ).exclude(status='completed').order_by('-token_number').first()

        next_token_num = (last_token.token_number + 1) if last_token else 1

        token = QueueToken.objects.create(
            student=student,
            faculty=faculty,
            token_number=next_token_num,
            request_type=request_type,
        )

        messages.success(request, f'You joined the queue! Your token number is #{token.token_number}.')
        return redirect('track_queue', token_id=token.id)

    faculties = Faculty.objects.all()
    return render(request, 'queue_app/join_queue.html', {
        'faculties': faculties,
        'selected_faculty': selected_faculty,
    })


@login_required
def track_queue(request, token_id):
    token = get_object_or_404(QueueToken, id=token_id)

    # How many people are ahead
    people_ahead = QueueToken.objects.filter(
        faculty=token.faculty,
        status='waiting',
        token_number__lt=token.token_number
    ).count()

    # Currently processing token
    current = QueueToken.objects.filter(
        faculty=token.faculty,
        status='processing'
    ).first()

    # Estimated wait: 5 minutes per person ahead
    estimated_wait = people_ahead * 5

    return render(request, 'queue_app/track_queue.html', {
        'token': token,
        'people_ahead': people_ahead,
        'current': current,
        'estimated_wait': estimated_wait,
    })