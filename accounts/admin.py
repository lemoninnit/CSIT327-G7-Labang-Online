from django.contrib import admin
from .models import User, OneTimeCode


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'full_name', 'email', 'contact_number',
        'barangay', 'is_email_verified', 'is_phone_verified', 'is_barangay_verified',
    )
    search_fields = ('username', 'full_name', 'email', 'contact_number')


@admin.register(OneTimeCode)
class OneTimeCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'purpose', 'code', 'created_at', 'expires_at', 'is_used')
    list_filter = ('purpose', 'is_used')

# Register your models here.
