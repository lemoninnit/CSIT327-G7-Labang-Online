from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

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
    nso_document = models.FileField(upload_to="nso_documents/")
    profile_photo = models.FileField(upload_to='profile_photos/', blank=True, null=True)
    resident_id_photo = models.FileField(upload_to='resident_ids/', blank=True, null=True)
    resident_confirmation = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    

    REQUIRED_FIELDS = ["email", "full_name", "contact_number", "date_of_birth"]
    civil_status = models.CharField(max_length=20, blank=True, null=True, choices=[
        ('Single','Single'), ('Married','Married'), ('Widowed','Widowed'), ('Separated','Separated'),
    ])

    def __str__(self):
        return self.username
