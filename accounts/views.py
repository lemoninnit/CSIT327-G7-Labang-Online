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
        action = request.POST.get('action') or 'otp'

        now = timezone.now()
        user = request.user if request.user.is_authenticated else None
        if not user:
            messages.error(request, 'Please log in to verify your account.')
            return redirect('accounts:register')

        if action == 'barangay':
            id_type = request.POST.get('id_type', '').strip()
            id_number = request.POST.get('id_number', '').strip()
            agree = request.POST.get('agree') == 'on'
            # file = request.FILES.get('id_photo')  # Could be stored if storage configured

            if not id_type or id_type == '':
                messages.error(request, 'Please select the Type of ID.')
            elif not id_number:
                messages.error(request, 'Please enter your ID Number.')
            elif not agree:
                messages.error(request, 'You must certify the statement to continue.')
            else:
                # In Sprint 1 we accept submission and mark the barangay verification as complete
                user.is_barangay_verified = True
                user.save(update_fields=['is_barangay_verified'])
                messages.success(request, 'Barangay Labangon verification submitted successfully.')

        else:
            email_code = request.POST.get('email_code', '').strip()
            phone_code = request.POST.get('phone_code', '').strip()

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

            # Only update the one they provided; both can still work
            if check_code('email', email_code):
                user.is_email_verified = True
            if check_code('phone', phone_code):
                user.is_phone_verified = True
            user.save(update_fields=['is_email_verified', 'is_phone_verified'])

        # Auto mark barangay as eligible if profile barangay is Labangon, unless already verified via modal
        if not user.is_barangay_verified and user.barangay and user.barangay.lower() == 'labangon':
            user.is_barangay_verified = True
            user.save(update_fields=['is_barangay_verified'])

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

        messages.info(request, 'Verification updated. Complete all steps to continue.')

    return render(request, 'accounts/verify.html')


def welcome(request: HttpRequest) -> HttpResponse:
    return render(request, 'accounts/welcome.html')

def barangay_certification(request: HttpRequest) -> HttpResponse:
    user = request.user if request.user.is_authenticated else None
    if not user:
        messages.error(request, 'Please log in to continue.')
        return redirect('accounts:register')

    if request.method == 'POST':
        id_type = request.POST.get('id_type', '').strip()
        id_number = request.POST.get('id_number', '').strip()
        agree = request.POST.get('agree') == 'on'

        if not id_type:
            messages.error(request, 'Please select the Type of ID.')
        elif not id_number:
            messages.error(request, 'Please enter your ID Number.')
        elif not agree:
            messages.error(request, 'You must agree to the terms & regulations.')
        else:
            user.is_barangay_verified = True
            user.save(update_fields=['is_barangay_verified'])
            messages.success(request, 'Barangay Labangon verification submitted successfully.')
            return redirect('accounts:verify')

    return render(request, 'accounts/barangay_cert.html')

# Create your views here.
