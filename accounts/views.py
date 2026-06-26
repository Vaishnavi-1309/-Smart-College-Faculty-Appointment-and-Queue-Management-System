from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def login_view(request):
    # If already logged in, go to dashboard
    if request.user.is_authenticated:
        role = request.user.role
        if role == 'student':
            return redirect('student_dashboard')
        elif role == 'faculty':
            return redirect('faculty_dashboard')
        elif role == 'admin':
            return redirect('/admin/')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            role = user.role
            if role == 'student':
                return redirect('student_dashboard')
            elif role == 'faculty':
                return redirect('faculty_dashboard')
            elif role == 'admin':
                return redirect('/admin/')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')

@login_required
def dashboard_view(request):
    role = request.user.role
    if role == 'student':
        return redirect('student_dashboard')
    elif role == 'faculty':
        return redirect('faculty_dashboard')
    elif role == 'admin':
        return redirect('/admin/')
    return redirect('login')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def student_dashboard(request):
    from accounts.models import Faculty
    from queue_app.models import QueueToken
    faculties = Faculty.objects.all()
    my_tokens = QueueToken.objects.filter(
        student=request.user.student
    ).exclude(status='completed').order_by('-created_at')
    return render(request, 'accounts/student_dashboard.html', {
        'faculties': faculties,
        'my_tokens': my_tokens,
    })


@login_required
def faculty_dashboard(request):
    from queue_app.models import QueueToken, Request
    faculty = request.user.faculty
    queue = QueueToken.objects.filter(
        faculty=faculty
    ).exclude(status='completed').order_by('token_number')
    current = queue.filter(status='processing').first()
    pending_requests = Request.objects.filter(faculty=faculty, status='pending')
    return render(request, 'accounts/faculty_dashboard.html', {
        'faculty': faculty,
        'queue': queue,
        'current': current,
        'pending_requests': pending_requests,
    })