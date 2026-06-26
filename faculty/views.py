from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import Faculty
from queue_app.models import QueueToken, Request


@login_required
def update_status(request):
    if request.method == 'POST':
        status = request.POST.get('status')
        faculty = request.user.faculty
        faculty.status = status
        faculty.save()
        messages.success(request, f'Status updated to: {faculty.get_status_display()}')
    return redirect('faculty_dashboard')


@login_required
def complete_token(request, token_id):
    token = get_object_or_404(QueueToken, id=token_id)
    token.status = 'completed'
    token.save()

    # Automatically start next token
    next_token = QueueToken.objects.filter(
        faculty=token.faculty,
        status='waiting'
    ).order_by('token_number').first()

    if next_token:
        next_token.status = 'processing'
        next_token.save()
        messages.success(request, f'Token {token.token_number} completed. Now calling Token {next_token.token_number}.')
    else:
        messages.success(request, f'Token {token.token_number} completed. No more students in queue.')

    return redirect('faculty_dashboard')


@login_required
def start_session(request):
    faculty = request.user.faculty

    # Check if already processing someone
    already_processing = QueueToken.objects.filter(
        faculty=faculty,
        status='processing'
    ).exists()

    if already_processing:
        messages.warning(request, 'Already processing a student. Complete current token first.')
        return redirect('faculty_dashboard')

    # Start the first waiting token
    first_token = QueueToken.objects.filter(
        faculty=faculty,
        status='waiting'
    ).order_by('token_number').first()

    if first_token:
        first_token.status = 'processing'
        first_token.save()
        messages.success(request, f'Now calling Token {first_token.token_number} — {first_token.student.name}')
    else:
        messages.info(request, 'No students in queue right now.')

    return redirect('faculty_dashboard')