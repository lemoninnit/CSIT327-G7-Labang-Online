from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mail

from .models import User, OneTimeCode
from .forms import RegistrationForm


def register(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user: User = form.save(commit=False)
            password = form.cleaned_data['password']
            user.set_password(password)
            user.is_active = True
            user.save()

            email_otp = OneTimeCode.create_code(user, 'email')
            phone_otp = OneTimeCode.create_code(user, 'phone')

            # Send verification email (console backend in development)
            send_mail(
                subject='Verify your email - Labang Online',
                message=f'Hi {user.full_name}, your email verification code is {email_otp.code}.',
                from_email=None,
                recipient_list=[user.email],
                fail_silently=True,
            )

            messages.success(request, 'Account created. Please verify your email and phone with the codes sent (console backend in dev).')
            login(request, user)
            return redirect('accounts:verify')
        else:
            return render(request, 'accounts/register.html', {'form': form})

    form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def verify(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        email_code = request.POST.get('email_code', '').strip()
        phone_code = request.POST.get('phone_code', '').strip()

        now = timezone.now()
        user = request.user if request.user.is_authenticated else None
        if not user:
            messages.error(request, 'Please log in to verify your account.')
            return redirect('accounts:register')

        def check_code(purpose: str, code_value: str) -> bool:
            if not code_value:
                return False
            try:
                otp = OneTimeCode.objects.filter(user=user, purpose=purpose, is_used=False).latest('created_at')
            except OneTimeCode.DoesNotExist:
                return False
            if otp.code != code_value:
                return False
            if otp.expires_at < now:
                return False
            otp.mark_used()
            return True

        if check_code('email', email_code):
            user.is_email_verified = True
        if check_code('phone', phone_code):
            user.is_phone_verified = True

        # Barangay verification simple flag (since barangay checked at registration)
        if user.barangay and user.barangay.lower() == 'labangon':
            user.is_barangay_verified = True

        user.save(update_fields=['is_email_verified', 'is_phone_verified', 'is_barangay_verified'])

        if user.is_email_verified and user.is_phone_verified and user.is_barangay_verified:
            # Send welcome email
            send_mail(
                subject='Welcome to Labang Online',
                message=f'Hi {user.full_name}, welcome to Labang Online! Your account is now verified.',
                from_email=None,
                recipient_list=[user.email],
                fail_silently=True,
            )
            messages.success(request, 'Verification complete. Welcome to Labang Online!')
            return redirect('accounts:welcome')

        messages.info(request, 'Codes processed. Complete all verifications to continue.')

    return render(request, 'accounts/verify.html')


def welcome(request: HttpRequest) -> HttpResponse:
    return render(request, 'accounts/welcome.html')

# Create your views here.
