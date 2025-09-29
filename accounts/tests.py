from django.test import TestCase
from django.utils import timezone
from .models import User, OneTimeCode


class RegistrationTest(TestCase):
    def test_create_user_and_otps(self):
        user = User.objects.create_user(username='u1', password='StrongPass123', email='u1@example.com', full_name='U One', address_line='A', barangay='Labangon', city='Cebu City', province='Cebu', contact_number='+639111111111')
        self.assertTrue(user.check_password('StrongPass123'))
        email_otp = OneTimeCode.create_code(user, 'email')
        phone_otp = OneTimeCode.create_code(user, 'phone')
        self.assertEqual(len(email_otp.code), 6)
        self.assertEqual(len(phone_otp.code), 6)
        self.assertGreater(email_otp.expires_at, timezone.now())

# Create your tests here.
