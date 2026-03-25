from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Complaint(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    )

    CATEGORY_CHOICES = (
        ('research', 'Research'),
        ('licensing', 'Licensing'),
        ('policy_regulations', 'Policy and Regulation'),
        ('standards', 'Standards'),
        ('numbering', 'Numbering'),
        ('billing', 'Billing'),
        ('internet_speed', 'Internet Speed'),
        ('other','Other')
    )

    name = models.CharField(max_length=255, help_text="Your full name")
    company = models.CharField(max_length=255, blank=True, null=True, help_text="Company name (optional)")
    telephone = models.CharField(max_length=20, help_text="Contact telephone number")
    email = models.EmailField(help_text="Email address")
    
    # Complaint Details
    complaint_text = models.TextField(help_text="Describe your complaint in detail")
    

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_complaints'
    )
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolution_summary = models.TextField(blank=True, null=True)
    investigation_notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    priority = models.CharField(
    max_length=10,
    choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
    default='medium'
    )

    resolved_at = models.DateTimeField(null=True, blank=True)

    sla_hours = models.IntegerField(default=48)

    def __str__(self):
        return self.title
    
class ComplaintUpdate(models.Model):
    """Audit trail for complaint updates"""
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='updates')
    comment = models.TextField()
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional: track status changes
    status_before = models.CharField(max_length=50, blank=True, null=True)
    status_after = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Update for {self.complaint.reference_number}"