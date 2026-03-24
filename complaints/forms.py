from django import forms
from .models import Complaint

class ComplaintForm(forms.ModelForm):
    
    
    class Meta:
        model = Complaint
        fields = ['name', 'company', 'telephone', 'email', 'category', 'complaint_text']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter your full name',
                'required': True
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Company name (optional)'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+267 1234 5678',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'your@email.com',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'complaint_text': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 5,
                'placeholder': 'Please describe your complaint in detail...',
                'required': True
            }),
        }