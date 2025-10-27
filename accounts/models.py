from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import secrets
import string

class User(AbstractUser):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    address_line = models.CharField(max_length=255)
    barangay = models.CharField(max_length=100, default="Labangon")
    city = models.CharField(max_length=100, default="Cebu City")
    province = models.CharField(max_length=100, default="Cebu")
    postal_code = models.CharField(max_length=10, default="6000")

    nso_document = models.BinaryField(blank=True, null=True)
    profile_photo = models.BinaryField(blank=True, null=True)
    resident_id_photo = models.BinaryField(blank=True, null=True)

    resident_confirmation = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    REQUIRED_FIELDS = ["email", "full_name", "contact_number", "date_of_birth"]
    civil_status = models.CharField(max_length=20, blank=True, null=True, choices=[
        ('Single','Single'), ('Married','Married'), ('Widowed','Widowed'), ('Separated','Separated'),
    ])

    def __str__(self):
        return self.username


class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    @classmethod
    def generate_code(cls, user):
        """Generate a new 6-digit verification code for the user"""
        # Delete any existing unused codes for this user
        cls.objects.filter(user=user, is_used=False).delete()
        
        # Generate a 6-digit code
        code = ''.join(secrets.choice(string.digits) for _ in range(6))
        
        # Create the reset code (expires in 10 minutes)
        from django.utils import timezone
        expires_at = timezone.now() + timezone.timedelta(minutes=10)
        
        return cls.objects.create(
            user=user,
            code=code,
            expires_at=expires_at
        )
    
    def is_valid(self):
        """Check if the code is still valid (not expired and not used)"""
        from django.utils import timezone
        return not self.is_used and timezone.now() < self.expires_at
    
    def __str__(self):
        return f"Reset code for {self.user.email}: {self.code}"

# Add this to your models.py file

class CertificateRequest(models.Model):
    CERTIFICATE_TYPES = [
        ('barangay_clearance', 'Barangay Clearance'),
        ('residency', 'Certificate of Residency'),
        ('indigency', 'Certificate of Indigency'),
        ('good_moral', 'Good Moral Character'),
        ('business_clearance', 'Business Clearance'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('failed', 'Failed Payment Verification'),
    ]
    
    PAYMENT_MODE = [
        ('gcash', 'GCash'),
        ('counter', 'Pay-on-the-Counter'),
    ]
    
    CLAIM_STATUS = [
        ('processing', 'Processing'),
        ('ready', 'Ready for Claim'),
        ('claimed', 'Claimed'),
    ]
    
    # Basic Info
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificate_requests')
    request_id = models.CharField(max_length=20, unique=True, editable=False)
    certificate_type = models.CharField(max_length=50, choices=CERTIFICATE_TYPES)
    
    # Request Details
    purpose = models.TextField()
    
    # Payment Info
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE, blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_reference = models.CharField(max_length=50, blank=True, null=True)
    
    # Claim Status
    claim_status = models.CharField(max_length=20, choices=CLAIM_STATUS, default='processing')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    claimed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.request_id:
            # Generate unique request ID (e.g., REQ-2025-0001)
            from django.utils import timezone
            year = timezone.now().year
            count = CertificateRequest.objects.filter(
                created_at__year=year
            ).count() + 1
            self.request_id = f"REQ-{year}-{count:04d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.request_id} - {self.get_certificate_type_display()}"