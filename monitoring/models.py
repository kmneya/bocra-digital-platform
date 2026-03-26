from django.db import models
from django.utils import timezone
from datetime import timedelta

class TelecomProvider(models.Model):
    """Telecommunication companies in Botswana"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    logo = models.ImageField(upload_to='providers/', blank=True, null=True)
    color = models.CharField(max_length=20, default='#87CEEB')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class NetworkQualityMetrics(models.Model):
    """Daily network quality monitoring data"""
    
    SERVICE_TYPES = (
        ('voice', 'Voice Call'),
        ('data', 'Data/Internet'),
        ('sms', 'SMS'),
    )
    
    REGIONS = (
        ('gaborone', 'Gaborone'),
        ('francistown', 'Francistown'),
        ('maun', 'Maun'),
        ('kanye', 'Kanye'),
        ('serowe', 'Serowe'),
        ('molepolole', 'Molepolole'),
        ('kasane', 'Kasane'),
        ('lobatse', 'Lobatse'),
        ('palapye', 'Palapye'),
        ('selibe_phikwe', 'Selibe Phikwe'),
        ('gantsi', 'Gantsi'),
        ('nahalapye', 'Mahalapye'),
        
    )
    
    provider = models.ForeignKey(TelecomProvider, on_delete=models.CASCADE, related_name='metrics')
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    region = models.CharField(max_length=50, choices=REGIONS)
    
    # QoS Metrics
    call_drop_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Call drop rate in percentage")
    call_setup_success_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Call setup success rate %")
    avg_throughput = models.DecimalField(max_digits=10, decimal_places=2, help_text="Average throughput in Mbps")
    latency = models.DecimalField(max_digits=10, decimal_places=2, help_text="Latency in milliseconds")
    jitter = models.DecimalField(max_digits=10, decimal_places=2, help_text="Jitter in milliseconds")
    packet_loss = models.DecimalField(max_digits=5, decimal_places=2, help_text="Packet loss percentage")
    
    # Availability
    uptime_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=99.9)
    downtime_minutes = models.IntegerField(default=0, help_text="Downtime in minutes")
    downtime_reason = models.CharField(max_length=255, blank=True, null=True)
    
    # Spectrum Analysis Data (JSON for complex data)
    spectrum_data = models.JSONField(default=dict, blank=True, help_text="Frequency spectrum analysis data")
    
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['provider', 'service_type', 'region', 'date']
        ordering = ['-date', 'provider', 'region']
    
    def __str__(self):
        return f"{self.provider.name} - {self.service_type} - {self.region} - {self.date}"


class NetworkIncident(models.Model):
    """Track network incidents and outages"""
    
    INCIDENT_TYPES = (
        ('planned', 'Planned Maintenance'),
        ('unplanned', 'Unplanned Outage'),
        ('degraded', 'Degraded Service'),
        ('full', 'Full Outage'),
    )
    
    SEVERITY = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    provider = models.ForeignKey(TelecomProvider, on_delete=models.CASCADE, related_name='incidents')
    title = models.CharField(max_length=255)
    incident_type = models.CharField(max_length=20, choices=INCIDENT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY)
    affected_services = models.CharField(max_length=255, help_text="Comma-separated list of affected services")
    affected_regions = models.TextField(help_text="Regions affected")
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    resolution_summary = models.TextField(blank=True, null=True)
    is_resolved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def duration_minutes(self):
        if self.end_time:
            return int((self.end_time - self.start_time).total_seconds() / 60)
        return int((timezone.now() - self.start_time).total_seconds() / 60)
    
    def __str__(self):
        return f"{self.provider.name} - {self.title} - {self.start_time}"


class SpectrumAnalysis(models.Model):
    """Spectrum analysis data for frequency monitoring"""
    
    provider = models.ForeignKey(TelecomProvider, on_delete=models.CASCADE, related_name='spectrum_data')
    frequency_band = models.CharField(max_length=50, help_text="e.g., 900MHz, 1800MHz, 2100MHz")
    measurement_date = models.DateTimeField(default=timezone.now)
    
    # Power measurements
    avg_power_dbm = models.DecimalField(max_digits=10, decimal_places=2, help_text="Average power in dBm")
    peak_power_dbm = models.DecimalField(max_digits=10, decimal_places=2, help_text="Peak power in dBm")
    noise_floor = models.DecimalField(max_digits=10, decimal_places=2, help_text="Noise floor in dBm")
    
    # Interference
    interference_detected = models.BooleanField(default=False)
    interference_type = models.CharField(max_length=100, blank=True, null=True)
    interference_power = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Full spectrum data (JSON for complex visualization)
    spectrum_snapshot = models.JSONField(default=dict, help_text="Full spectrum data points")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.provider.name} - {self.frequency_band} - {self.measurement_date}"