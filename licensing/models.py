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
        ('cellular_lis','Cellular License'),
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
        return f"{self.business_name} - {self.license_type.name}"
    

class AircraftRadioLicense(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE,)

    # 🔹 APPLICANT DETAILS
    client_type = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    nationality = models.CharField(max_length=100)
    company_reg_number = models.CharField(max_length=100, blank=True, null=True)

    email = models.EmailField()
    phone = models.CharField(max_length=20)

    # 🔹 BASE STATION
    station_name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    latitude = models.CharField(max_length=50)
    longitude = models.CharField(max_length=50)

    # 🔹 EQUIPMENT
    equipment_type = models.CharField(max_length=100)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100)

    # 🔹 STATUS TRACKING (IMPORTANT)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('under_review', 'Under Review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)