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
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES,)
    title = models.CharField(max_length=255)
    description = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_complaints'
    )

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
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='updates')
    comment = models.TextField()
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"Update for {self.complaint.id}"