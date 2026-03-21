from django import forms
from .models import LicenseApplication

class LicenseForm(forms.ModelForm):
    class Meta:
        model = LicenseApplication
        fields = ['business_name', 'license_type']