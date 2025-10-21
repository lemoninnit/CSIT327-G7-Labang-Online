#!/usr/bin/env python
"""
Gmail Password Recovery Setup Script
This script helps you configure and test the Gmail password recovery system
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labang_online.settings')
django.setup()

from django.core.mail import send_mail
from accounts.models import User, PasswordResetCode

def setup_gmail_recovery():
    """Setup and test the Gmail password recovery system"""
    print("Setting up Gmail Password Recovery System")
    print("=" * 50)
    
    # Check current email configuration
    print("Current Email Configuration:")
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER or 'Not set'}")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()
    
    # Check if Gmail is configured
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        print("WARNING: Gmail configuration incomplete!")
        print("   Please set the following environment variables:")
        print("   - EMAIL_HOST_USER=your_gmail@gmail.com")
        print("   - EMAIL_HOST_PASSWORD=your_16_character_app_password")
        print("   - EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend")
        print()
        print("   See GMAIL_SETUP_GUIDE.md for detailed instructions.")
        return False
    
    # Test email sending
    print("Testing email configuration...")
    try:
        send_mail(
            'Labang Online - Password Recovery Test',
            'This is a test email to verify your Gmail SMTP configuration is working correctly.',
            settings.DEFAULT_FROM_EMAIL,
            [settings.EMAIL_HOST_USER],  # Send to yourself
            fail_silently=False,
        )
        print("SUCCESS: Email sent successfully!")
        print("   Check your Gmail inbox for the test email.")
        print()
    except Exception as e:
        print(f"ERROR: Failed to send email: {str(e)}")
        print("   Please check your Gmail app password and configuration.")
        return False
    
    # Test password recovery flow
    print("Testing password recovery flow...")
    try:
        # Create a test user if none exists
        test_user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'full_name': 'Test User',
                'contact_number': '1234567890',
                'date_of_birth': '1990-01-01',
                'address_line': 'Test Address',
                'password': 'testpass123'
            }
        )
        
        if created:
            print("   Created test user for demonstration")
        
        # Generate a test reset code
        reset_code = PasswordResetCode.generate_code(test_user)
        print(f"   Generated test reset code: {reset_code.code}")
        print(f"   Code expires at: {reset_code.expires_at}")
        print(f"   Code is valid: {reset_code.is_valid()}")
        
        # Clean up test data
        reset_code.delete()
        if created:
            test_user.delete()
            
        print("SUCCESS: Password recovery system is working correctly!")
        print()
        
    except Exception as e:
        print(f"ERROR: Password recovery test failed: {str(e)}")
        return False
    
    print("Setup Complete!")
    print("=" * 50)
    print("Your Gmail password recovery system is ready!")
    print()
    print("Next steps:")
    print("1. Start your Django server: python manage.py runserver")
    print("2. Go to /accounts/forgot_password/ to test the flow")
    print("3. Enter a registered email address")
    print("4. Check Gmail for the 6-digit verification code")
    print("5. Enter the code and set a new password")
    print()
    print("Available URLs:")
    print("   - Forgot Password: /accounts/forgot_password/")
    print("   - Verify Code: /accounts/verify_code/<user_id>/")
    print("   - Reset Password: /accounts/reset_password/")
    
    return True

if __name__ == "__main__":
    setup_gmail_recovery()
