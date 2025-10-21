"""
Load environment variables and test email configuration
"""
import os
import sys
import django
from dotenv import load_dotenv
from django.core.mail import send_mail
from django.conf import settings

# Load environment variables from .env file
load_dotenv()

# Print loaded environment variables (without showing the actual password)
print("Environment variables loaded:")
print(f"EMAIL_HOST_USER: {os.getenv('EMAIL_HOST_USER')}")
print(f"EMAIL_BACKEND: {os.getenv('EMAIL_BACKEND')}")
print("EMAIL_HOST_PASSWORD: [Hidden for security]")

# Configure Django settings for email
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labang_online.settings')
django.setup()

# Test sending an email
def test_email(recipient_email):
    """Send a test email to verify configuration"""
    try:
        send_mail(
            subject="Test Email from Labang Online",
            message="This is a test email to verify your email configuration is working correctly.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        print(f"\nTest email sent successfully to {recipient_email}!")
        return True
    except Exception as e:
        print(f"\nError sending test email: {str(e)}")
        return False

if __name__ == "__main__":
    # If an email address is provided as a command line argument, use it
    # Otherwise, use the EMAIL_HOST_USER as the recipient
    recipient = sys.argv[1] if len(sys.argv) > 1 else os.getenv('EMAIL_HOST_USER')
    test_email(recipient)