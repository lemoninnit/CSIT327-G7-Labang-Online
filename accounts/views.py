from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.core.mail import send_mail

from .models import User
from .forms import RegistrationForm

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.views.decorators.cache import never_cache
import base64

from django.shortcuts import render


User = get_user_model()

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
        messages.success(request, f"Password reset instructions have been sent to {email} if an account exists with this email address.")
    return render(request, 'accounts/forgot_password.html')


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