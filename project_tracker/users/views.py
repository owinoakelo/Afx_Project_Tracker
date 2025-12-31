from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import User
import random
import string


def generate_otp(length=6):
    """Generate a random OTP code."""
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(user, otp_code):
    """Send OTP to user's email."""
    subject = 'Your OTP Code'
    message = f'Your OTP code is: {otp_code}\n\nThis code will expire in 10 minutes.'
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send OTP email: {e}")
        return False


@require_http_methods(["GET", "POST"])
def request_otp(request):
    """Request an OTP to be sent to the user's email."""
    if request.method == 'GET':
        return render(request, 'users/request_otp.html')
    
    email = request.POST.get('email')
    if not email:
        return render(request, 'users/request_otp.html', {'error': 'Email is required.'})
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # For security, don't reveal if user exists
        # return render(request, 'users/request_otp.html', 
        return redirect('users:verify_otp')
                    #  {'message': 'If the email exists, an OTP has been sent.'})
    
    # Generate and send OTP
    otp_code = generate_otp()
    user.set_otp(otp_code)
    
    if send_otp_email(user, otp_code):
        request.session['otp_email'] = email
        return redirect('users:verify_otp')
    else:
        return render(request, 'users/request_otp.html', 
                     {'error': 'Failed to send OTP. Please try again.'})


@require_http_methods(["GET", "POST"])
def verify_otp(request):
    """Verify the OTP code entered by the user."""
    if request.method == 'GET':
        return render(request, 'users/verify_otp.html')
    
    email = request.session.get('otp_email')
    otp_code = request.POST.get('otp_code')
    
    if not email or not otp_code:
        return render(request, 'users/verify_otp.html', 
                     {'error': 'Email and OTP code are required.'})
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return render(request, 'users/verify_otp.html', 
                     {'error': 'User not found.'})
    
    # Verify OTP
    if user.otp_code != otp_code:
        return render(request, 'users/verify_otp.html', 
                     {'error': 'Invalid OTP code.'})
    
    if not user.is_otp_valid():
        return render(request, 'users/verify_otp.html', 
                     {'error': 'OTP has expired. Please request a new one.'})
    
    # OTP verified successfully
    user.is_otp_verified = True
    user.otp_code = None
    user.otp_expiry = None
    user.save()
    
    # Log the user in
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    request.session.pop('otp_email', None)
    
    return redirect('index')  # or your home page


@login_required
def logout_user(request):
    """Log out the user."""
    logout(request)
    return redirect('users:request_otp')


def create_user(request):
    """Create a new user."""
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        print(f"Creating user with Email: {email}, First Name: {first_name}, Last Name: {last_name}")

        user = User.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            username=email  
        )
        user.set_unusable_password()
        user.save()
    return render(request, 'users/create_user.html')

def login_page(request):
    """Redirect to request OTP page."""
    return redirect('users:request_otp')