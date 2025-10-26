"""
Views for Labang Online application
Handles authentication, user management, and password recovery
"""

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
import base64

from django.shortcuts import render
from .models import User, PasswordResetCode
from .forms import RegistrationForm

# -------------------- HELPER FUNCTION --------------------
def get_base64_image(data):
    """Convert binary image data to base64 string WITHOUT data URI prefix"""
    if data:
        return base64.b64encode(data).decode('utf-8')
    return None


# -------------------- LOGIN --------------------
@never_cache
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.resident_confirmation:  # Only allow verified users
                auth_login(request, user)
                return redirect('accounts:personal_info')
            else:
                messages.warning(request, "Account verification pending. Please visit Barangay Hall of Labangon to complete your account verification.")
        else:
            messages.error(request, "Invalid credentials. Please check your username and password and try again.")

    return render(request, 'accounts/login.html')


# -------------------- REGISTER --------------------
@never_cache
def register(request):
    if request.method == "POST":
        # Get form data
        full_name = request.POST.get("full_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        contact_number = request.POST.get("contact_number")
        date_of_birth = request.POST.get("date_of_birth")
        address_line = request.POST.get("address_line")
        barangay = request.POST.get("barangay", "Labangon")
        city = request.POST.get("city", "Cebu City")
        province = request.POST.get("province", "Cebu")
        postal_code = request.POST.get("postal_code", "6000")
        password = request.POST.get("password")
        resident_confirmation = request.POST.get("resident_confirmation") == "on"
        nso_document = request.FILES.get("nso_document")

        # Check if email or username already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "This email address is already registered. Please use a different email or log in to your existing account.")
            return render(request, "accounts/register.html")
        if User.objects.filter(username=username).exists():
            messages.error(request, "This username is already taken. Please choose a different username.")
            return render(request, "accounts/register.html")

        # Create the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            contact_number=contact_number,
            date_of_birth=date_of_birth,
            address_line=address_line,
            barangay=barangay,
            city=city,
            province=province,
            postal_code=postal_code,
            resident_confirmation=resident_confirmation,
            nso_document=nso_document.read() if nso_document else None,
        )

        messages.success(request, "Account created successfully! Please proceed to Barangay Hall of Labangon for verification.")
        return redirect("accounts:login")

    return render(request, "accounts/register.html")


# -------------------- WELCOME PAGE --------------------
def welcome(request: HttpRequest) -> HttpResponse:
    return render(request, 'accounts/welcome.html')


# -------------------- FORGOT PASSWORD --------------------
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Generate verification code
            reset_code = PasswordResetCode.generate_code(user)
            
            # Send email with verification code
            subject = 'Password Reset Verification Code - Labang Online'
            message = f"""
            Hello {user.full_name},
            
            You requested a password reset for your Labang Online account.
            
            Your verification code is: {reset_code.code}
            
            This code will expire in 10 minutes.
            
            If you didn't request this password reset, please ignore this email.
            
            Best regards,
            Labang Online Team
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, f"Verification code sent to {email}. Please check your email and enter the 6-digit code.")
                return redirect('accounts:verify_code', user_id=user.id)
            except Exception as e:
                messages.error(request, f"Failed to send email. Please try again later. Error: {str(e)}")
                
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            messages.success(request, f"If an account exists with {email}, a verification code has been sent.")
            return redirect('accounts:login')
    
    return render(request, 'accounts/forgot_password.html')


# -------------------- VERIFY CODE --------------------
def verify_code(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        entered_code = request.POST.get('code')
        
        try:
            reset_code = PasswordResetCode.objects.get(
                user=user, 
                code=entered_code, 
                is_used=False
            )
            
            if reset_code.is_valid():
                # Store the code in session for password reset
                request.session['reset_code_id'] = reset_code.id
                messages.success(request, "Code verified successfully! Please enter your new password.")
                return redirect('accounts:reset_password')
            else:
                messages.error(request, "Code has expired. Please request a new code.")
                return redirect('accounts:forgot_password')
                
        except PasswordResetCode.DoesNotExist:
            messages.error(request, "Invalid verification code. Please try again.")
    
    context = {'user': user}
    return render(request, 'accounts/verify_code.html', context)


# -------------------- RESET PASSWORD --------------------
def reset_password(request):
    if 'reset_code_id' not in request.session:
        messages.error(request, "No active password reset session. Please start over.")
        return redirect('accounts:forgot_password')
    
    try:
        reset_code = PasswordResetCode.objects.get(
            id=request.session['reset_code_id'],
            is_used=False
        )
        
        if not reset_code.is_valid():
            messages.error(request, "Reset session expired. Please request a new code.")
            del request.session['reset_code_id']
            return redirect('accounts:forgot_password')
            
    except PasswordResetCode.DoesNotExist:
        messages.error(request, "Invalid reset session. Please start over.")
        del request.session['reset_code_id']
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/reset_password.html')
        
        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, 'accounts/reset_password.html')
        
        # Update user password
        reset_code.user.set_password(new_password)
        reset_code.user.save()
        
        # Mark code as used
        reset_code.is_used = True
        reset_code.save()
        
        # Clear session
        del request.session['reset_code_id']
        
        messages.success(request, "Password updated successfully! You can now log in with your new password.")
        return redirect('accounts:login')
    
    return render(request, 'accounts/reset_password.html')


# -------------------- LOGOUT CONFIRM --------------------
@login_required(login_url='accounts:login')
@never_cache
def logout_confirm(request):
    if request.method == 'POST':
        auth_logout(request)
        messages.success(request, "You have successfully logged out.")
        return redirect('accounts:login')
    return render(request, 'accounts/logout_confirm.html')


# -------------------- PERSONAL INFO --------------------
@login_required(login_url='accounts:login')
@never_cache
def personal_info(request):
    user = request.user

    # Convert to base64 (without data URI prefix - template adds it)
    profile_pic_base64 = get_base64_image(user.profile_photo)
    resident_id_base64 = get_base64_image(user.resident_id_photo)

    context = {
        'user': user,
        'profile_pic_base64': profile_pic_base64,
        'resident_id_base64': resident_id_base64,
    }   
    return render(request, 'accounts/personal_info.html', context)


# -------------------- EDIT PROFILE --------------------
@login_required(login_url='accounts:login')
@never_cache
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        # Update text fields
        user.full_name = request.POST.get('full_name', user.full_name)
        user.contact_number = request.POST.get('contact_number', user.contact_number)
        user.address_line = request.POST.get('address_line', user.address_line)
        
        # Handle date_of_birth
        date_of_birth = request.POST.get('date_of_birth')
        if date_of_birth:
            user.date_of_birth = date_of_birth
            
        # Handle civil_status
        civil_status = request.POST.get('civil_status')
        if civil_status:
            user.civil_status = civil_status

        # Handle file uploads
        profile_photo = request.FILES.get('profile_photo')
        if profile_photo:
            user.profile_photo = profile_photo.read()

        resident_id_photo = request.FILES.get('resident_id_photo')
        if resident_id_photo:
            user.resident_id_photo = resident_id_photo.read()

        nso_document = request.FILES.get('nso_document')
        if nso_document:
            user.nso_document = nso_document.read()

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('accounts:personal_info')  # Redirect to personal_info after save

    # Convert images to base64 for display
    profile_pic_base64 = get_base64_image(user.profile_photo)
    resident_id_base64 = get_base64_image(user.resident_id_photo)

    context = {
        'user': user,
        'profile_pic_base64': profile_pic_base64,
        'resident_id_base64': resident_id_base64,
    }
    return render(request, 'accounts/edit_profile.html', context)


# -------------------- VIEW COMPLETE PROFILE --------------------
@login_required(login_url='accounts:login')
@never_cache
def complete_profile(request):
    user = request.user
    
    # Convert images to base64
    profile_pic_base64 = get_base64_image(user.profile_photo)
    resident_id_base64 = get_base64_image(user.resident_id_photo)
    
    # If you have a Dependent model, fetch dependents here
    dependents = []
    
    context = {
        'user': user,
        'profile_pic_base64': profile_pic_base64,
        'resident_id_base64': resident_id_base64,
        'dependents': dependents,
    }
    return render(request, 'accounts/complete_profile.html', context)


@login_required(login_url='accounts:login')
@never_cache
def document_request(request):
    user = request.user
    profile_pic_base64 = get_base64_image(user.profile_photo)
    
    context = {
        'user': user,
        'profile_pic_base64': profile_pic_base64,
    }
    return render(request, 'accounts/document_request.html', context)


@login_required(login_url='accounts:login')
@never_cache
def certificate_requests(request):
    user = request.user
    profile_pic_base64 = get_base64_image(user.profile_photo)
    
    # Fetch user's certificate requests here
    # requests = CertificateRequest.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'user': user,
        'profile_pic_base64': profile_pic_base64,
        # 'requests': requests,
    }
    return render(request, 'accounts/certificate_requests.html', context)