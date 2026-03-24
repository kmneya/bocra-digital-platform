from django import forms
from .models import LicenseApplication, AircraftRadioLicense,CellularLicense

class LicenseForm(forms.ModelForm):
    class Meta:
        model = LicenseApplication
        fields = ['business_name', 'license_type', 'details']
        widgets = {
            'details': forms.Textarea(attrs={'rows': 4}),
        }

class AircraftRadioLicenseForm(forms.ModelForm):
    class Meta:
        model = AircraftRadioLicense
        fields = [
            'name', 'nationality', 'email', 'phone',
            'station_name', 'city', 'latitude', 'longitude',
            'equipment_type', 'make', 'model', 'serial_number'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'station_name': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.TextInput(attrs={'class': 'form-control'}),
            'longitude': forms.TextInput(attrs={'class': 'form-control'}),
            'equipment_type': forms.TextInput(attrs={'class': 'form-control'}),
            'make': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

    # Add this to your licensing/forms.py

class CellularLicenseForm(forms.ModelForm):
    """Simple cellular license application form"""
    
    class Meta:
        model = CellularLicense
        exclude = ['application', 'user', 'created_at']
        widgets = {
            'site_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Gaborone Central Tower'
            }),
            'site_location': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Gaborone, Botswana'
            }),
            'equipment_type': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', 'Select equipment type'),
                ('Base Station', 'Base Station'),
                ('Repeater', 'Repeater'),
                ('Small Cell', 'Small Cell'),
                ('Micro Cell', 'Micro Cell'),
            ]),
            'frequency_band': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', 'Select frequency band'),
                ('900MHz', '900MHz (2G/3G)'),
                ('1800MHz', '1800MHz (2G/4G)'),
                ('2100MHz', '2100MHz (3G/4G)'),
                ('2600MHz', '2600MHz (4G)'),
                ('3500MHz', '3500MHz (5G)'),
            ]),
            'service_type': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', 'Select service type'),
                ('GSM', 'GSM (2G)'),
                ('UMTS', 'UMTS (3G)'),
                ('LTE', 'LTE (4G)'),
                ('5G', '5G'),
                ('IoT', 'IoT/M2M'),
            ]),
            'coverage_area': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Describe the intended coverage area (e.g., Central Business District, residential areas within 5km radius)'
            }),
        }