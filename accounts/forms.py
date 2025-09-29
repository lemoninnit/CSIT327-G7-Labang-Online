from django import forms
from .models import User


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'full_name', 'username', 'email', 'contact_number',
            'date_of_birth', 'address_line', 'barangay', 'city', 'province', 'postal_code',
        ]

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        password_confirm = cleaned.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Passwords do not match.')
        if cleaned.get('barangay', '').lower() != 'labangon':
            self.add_error('barangay', 'Registration is limited to Barangay Labangon residents.')
        return cleaned


