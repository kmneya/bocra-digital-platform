from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class LicenseType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class LicenseApplication(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='license_applications')
    license_type = models.ForeignKey(LicenseType, on_delete=models.CASCADE)

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