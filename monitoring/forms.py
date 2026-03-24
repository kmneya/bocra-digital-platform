from django import forms
from .models import NetworkQualityMetrics, NetworkIncident, SpectrumAnalysis

class NetworkQualityMetricsForm(forms.ModelForm):
    class Meta:
        model = NetworkQualityMetrics
        fields = '__all__'
        widgets = {
            'provider': forms.Select(attrs={'class': 'form-select'}),
            'service_type': forms.Select(attrs={'class': 'form-select'}),
            'region': forms.Select(attrs={'class': 'form-select'}),
            'call_drop_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'call_setup_success_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'avg_throughput': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'latency': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'jitter': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'packet_loss': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'uptime_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'downtime_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'downtime_reason': forms.TextInput(attrs={'class': 'form-control'}),
        }