from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class LicenseApplication(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    LICENSE_CHOICES = (
        ('aircraft_radio','Aircraft Radio License'),
        ('amateur_rad_lis','Amateur Radio License'),
        ('broadcasting_lis','Broadcasting License'),
        ('cellular_details','Cellular License'),
        ('citizen_band_rad_lis','Citizen Band Radio License'),
        ('vans_lis','VANS License'),
        ('point_to_to_lis','Point-to-Point Lisense'),
        ('satellite_service_lis','Satellite Service License'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='license_applications')
    license_type = models.CharField(max_length=50, choices=LICENSE_CHOICES,)

    business_name = models.CharField(max_length=255)
    details = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    review_notes = models.TextField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.business_name} - {self.license_type}"
    

class AircraftRadioLicense(models.Model):
    # Link to main application
    application = models.OneToOneField(
        LicenseApplication, 
        on_delete=models.CASCADE, 
        related_name='aircraft_details'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Applicant Details
    client_type = models.CharField(max_length=50, default='person')
    name = models.CharField(max_length=255)
    nationality = models.CharField(max_length=100)
    company_reg_number = models.CharField(max_length=100, blank=True, null=True)

    email = models.EmailField()
    phone = models.CharField(max_length=20)

    # Base Station
    station_name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)

    # Equipment
    equipment_type = models.CharField(max_length=100)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Aircraft Radio - {self.name}"

    # Add this to your licensing/models.py

class CellularLicense(models.Model):
    """
    Cellular License Application - Demonstrates BOCRA's capability to handle 
    specialized telecommunications licensing requirements
    """
    
    # Link to the main application
    application = models.OneToOneField(
        LicenseApplication, 
        on_delete=models.CASCADE, 
        related_name='cellular_details'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Key cellular license fields (demonstrating specialized requirements)
    
    # 1. Site Information
    site_name = models.CharField(max_length=255, help_text="Name of the cellular site/station")
    site_location = models.CharField(max_length=255, help_text="Location/city where equipment will be installed")
    
    # 2. Equipment Details
    equipment_type = models.CharField(max_length=100, help_text="Type of cellular equipment (e.g., Base Station, Repeater)")
    
    # 3. Technical Specifications
    frequency_band = models.CharField(max_length=50, help_text="Operating frequency band (e.g., 900MHz, 1800MHz, 2100MHz)")
    
    # 4. Service Type
    service_type = models.CharField(max_length=50, help_text="Type of cellular service (e.g., GSM, LTE, 5G)")
    
    # 5. Coverage Area
    coverage_area = models.TextField(blank=True, null=True, help_text="Description of intended coverage area")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Cellular License"
        verbose_name_plural = "Cellular Licenses"
    
    def __str__(self):
        return f"Cellular License - {self.site_name} - {self.frequency_band}"