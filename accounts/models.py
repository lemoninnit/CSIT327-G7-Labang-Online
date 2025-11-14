from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
import secrets
import string
import uuid


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

    # UPDATED: Changed from BinaryField to URLField for Supabase Storage

    profile_photo_url = models.URLField(blank=True, null=True)
    resident_id_photo_url = models.URLField(blank=True, null=True)

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
        
        # Create the reset code (expires in 5 minutes)
        from django.utils import timezone
        expires_at = timezone.now() + timezone.timedelta(minutes=5)
        
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


class CertificateRequest(models.Model):
    CERTIFICATE_TYPES = [
        ('barangay_clearance', 'Barangay Clearance'),
        ('residency', 'Certificate of Residency'),
        ('indigency', 'Certificate of Indigency'),
        ('good_moral', 'Good Moral Character'),
        ('business_clearance', 'Business Clearance'),
    ]
    
    PAYMENT_STATUS = [
        ('unpaid', 'Unpaid'),
        ('pending', 'Pending Verification'),
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
    
    # UPDATED: Changed from BinaryField to URLField for Supabase Storage
    proof_photo_url = models.URLField(blank=True, null=True)
    
    # Business Details
    business_name = models.CharField(max_length=255, blank=True, null=True)
    business_type = models.CharField(max_length=50, blank=True, null=True)
    business_nature = models.CharField(max_length=255, blank=True, null=True)
    business_address = models.TextField(blank=True, null=True)
    employees_count = models.PositiveIntegerField(blank=True, null=True)
    
    # Payment Info
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='unpaid')
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
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['certificate_type']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.request_id:
            # Generate unique request ID (e.g., REQ-2025-0001)
            from django.utils import timezone
            import random
            year = timezone.now().year
            
            # Try to generate a unique request ID with retry logic
            max_attempts = 100
            for attempt in range(max_attempts):
                # Get the highest existing number for this year
                existing_requests = CertificateRequest.objects.filter(
                    request_id__startswith=f"REQ-{year}-"
                ).order_by('-request_id').first()
                
                if existing_requests:
                    # Extract the number from the last request ID
                    try:
                        last_number = int(existing_requests.request_id.split('-')[-1])
                        next_number = last_number + 1
                    except (ValueError, IndexError):
                        next_number = 1
                else:
                    next_number = 1
                
                # Add some randomness to avoid collisions in concurrent requests
                if attempt > 0:
                    next_number += random.randint(1, 10)
                
                self.request_id = f"REQ-{year}-{next_number:04d}"
                
                # Check if this ID already exists
                if not CertificateRequest.objects.filter(request_id=self.request_id).exists():
                    break
            else:
                # If we couldn't generate a unique ID after max_attempts, use timestamp
                import time
                timestamp = int(time.time() * 1000) % 10000
                self.request_id = f"REQ-{year}-{timestamp:04d}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.request_id} - {self.get_certificate_type_display()}"


class IncidentReport(models.Model):
    REPORT_TYPES = [
        ('Theft', 'Theft'),
        ('Assault', 'Assault'),
        ('Vandalism', 'Vandalism'),
        ('Disturbance', 'Disturbance'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Under Investigation', 'Under Investigation'),
        ('Mediation Scheduled', 'Mediation Scheduled'),
        ('Resolved', 'Resolved'),
    ]

    report_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='incident_reports')
    incident_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    place = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]

    def save(self, *args, **kwargs):
        if not self.report_id:
            self.report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.report_id} - {self.incident_type}"
    


class Announcement(models.Model):
    ANNOUNCEMENT_TYPES = [
        ('general', 'General Announcement'),
        ('event', 'Event'),
        ('alert', 'Alert'),
        ('maintenance', 'Maintenance'),
    ]
    
    title = models.CharField(max_length=255)
    content = models.TextField()
    announcement_type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPES, default='general')
    is_active = models.BooleanField(default=True)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%Y-%m-%d')}"