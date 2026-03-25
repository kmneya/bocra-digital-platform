from django import forms
from .models import PaymentTransaction, PaymentMethod

class PaymentForm(forms.ModelForm):
    """Payment form for license applications"""
    
    class Meta:
        model = PaymentTransaction
        fields = ['payment_method', 'payment_type', 'amount', 'description']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].queryset = PaymentMethod.objects.filter(is_active=True)
        self.fields['amount'].widget.attrs['readonly'] = True


class PaymentConfirmationForm(forms.Form):
    """Form to confirm payment (simulated gateway)"""
    payment_reference = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter payment reference number'})
    )
    payment_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )