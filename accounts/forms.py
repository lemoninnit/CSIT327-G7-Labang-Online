from django import forms
from .models import User


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'full_name',
            'date_of_birth',
            'address_line',
            'barangay',
            'city',
            'province',
            'contact_number',
            'password'
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


