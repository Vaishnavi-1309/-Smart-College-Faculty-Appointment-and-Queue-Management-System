from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import Faculty
from queue_app.models import QueueToken, Request
import qrcode
import io
import base64


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
    from queue_app.views import send_turn_notification

    token = get_object_or_404(QueueToken, id=token_id)
    token.status = 'completed'
    token.save()

    # Get next waiting token
    next_token = QueueToken.objects.filter(
        faculty=token.faculty,
        status='waiting'
    ).order_by('token_number').first()

    if next_token:
        next_token.status = 'processing'
        next_token.save()
        messages.success(request, f'Token {token.token_number} completed. Now calling Token {next_token.token_number}.')

        # Send email to student who is 2nd in queue
        second_token = QueueToken.objects.filter(
            faculty=token.faculty,
            status='waiting'
        ).order_by('token_number').first()

        if second_token:
            send_turn_notification(second_token)

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

@login_required
def get_qr_code(request):
    faculty = request.user.faculty
    
    # URL that student will be taken to when they scan
    join_url = request.build_absolute_uri(f'/queue/join/?faculty_id={faculty.id}')
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(join_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 so we can show in HTML
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return render(request, 'faculty/qr_code.html', {
        'faculty': faculty,
        'qr_image': img_base64,
        'join_url': join_url,
    })