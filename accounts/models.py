from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    address_line = models.CharField(max_length=255)
    barangay = models.CharField(max_length=100)
    city = models.CharField(max_length=100, default='Cebu City')
    province = models.CharField(max_length=100, default='Cebu')
    postal_code = models.CharField(max_length=10, blank=True)
    contact_number = models.CharField(max_length=32)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    is_barangay_verified = models.BooleanField(default=False)


class OneTimeCode(models.Model):
    PURPOSE_CHOICES = [
        ('email', 'Email Verification'),
        ('phone', 'Phone Verification'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    purpose = models.CharField(max_length=16, choices=PURPOSE_CHOICES)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def mark_used(self) -> None:
        self.is_used = True
        self.save(update_fields=['is_used'])

    @classmethod
    def create_code(cls, user: 'User', purpose: str, ttl_minutes: int = 10) -> 'OneTimeCode':
        expires = timezone.now() + timezone.timedelta(minutes=ttl_minutes)
        from random import randint
        code = f"{randint(0, 999999):06d}"
        return cls.objects.create(user=user, purpose=purpose, code=code, expires_at=expires)

# Create your models here.
