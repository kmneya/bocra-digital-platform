from django import forms
from .models import Complaint

class ComplaintForm(forms.ModelForm):
    """Complaint form with auto-population for returning users"""
    
    class Meta:
        model = Complaint
        fields = ['name', 'company', 'telephone', 'email', 'category', 'complaint_text']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name (optional)'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+267 1234 5678'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'complaint_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Please describe your complaint in detail...'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Get the user's last complaint to auto-populate fields
            last_complaint = Complaint.objects.filter(user=user).order_by('-created_at').first()
            
            if last_complaint:
                # Auto-populate fields from last complaint
                self.initial['name'] = last_complaint.name
                self.initial['telephone'] = last_complaint.telephone
                self.initial['email'] = last_complaint.email
                self.initial['company'] = last_complaint.company
                
                # Make these fields read-only
                self.fields['name'].widget.attrs['readonly'] = True
                self.fields['telephone'].widget.attrs['readonly'] = True
                self.fields['email'].widget.attrs['readonly'] = True
                self.fields['company'].widget.attrs['readonly'] = True
                
                # Add a note that fields are auto-filled
                self.fields['name'].help_text = "Auto-filled from your previous complaint"
                self.fields['telephone'].help_text = "Auto-filled from your previous complaint"
                self.fields['email'].help_text = "Auto-filled from your previous complaint"