from django.db import models
from django.conf import settings
from django.utils import timezone
from licensing.models import LicenseApplication

User = settings.AUTH_USER_MODEL

class PaymentMethod(models.Model):
    """Payment methods available"""
    METHOD_CHOICES = (
        ('mobile_money', 'Mobile Money'),
        ('credit_card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash (In-Person)'),
    )
    
    name = models.CharField(max_length=50, choices=METHOD_CHOICES)
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="FontAwesome icon class")
    
    def __str__(self):
        return self.get_name_display()


class PaymentTransaction(models.Model):
    """Payment transactions for license applications"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_TYPE_CHOICES = (
        ('license_fee', 'License Application Fee'),
        ('renewal', 'License Renewal'),
        ('amendment', 'License Amendment'),
        ('type_approval', 'Type Approval Fee'),
        ('other', 'Other'),
    )
    
    # Reference numbers
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, editable=False)
    reference_number = models.CharField(max_length=50, unique=True, blank=True, editable=False)
    
    # Links
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    license_application = models.ForeignKey(
        LicenseApplication, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='payments'
    )
    
    # Payment details
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPE_CHOICES, default='license_fee')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='BWP')
    
    # Description
    description = models.TextField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment details (stored from gateway response)
    payment_gateway = models.CharField(max_length=50, blank=True, null=True)
    gateway_reference = models.CharField(max_length=200, blank=True, null=True)
    gateway_response = models.JSONField(default=dict, blank=True, help_text="Raw response from payment gateway")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    
    # Receipt
    receipt_number = models.CharField(max_length=100, blank=True, null=True)
    receipt_file = models.FileField(upload_to='payments/receipts/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            import random
            import string
            date_str = timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.digits, k=6))
            self.transaction_id = f"BOCRA-PAY-{date_str}-{random_str}"
        
        if not self.reference_number and self.license_application:
            self.reference_number = f"INV-{self.license_application.id}-{self.transaction_id[-6:]}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.user.username} - {self.amount} BWP"


class PaymentReceipt(models.Model):
    """Payment receipts and invoices"""
    
    transaction = models.OneToOneField(PaymentTransaction, on_delete=models.CASCADE, related_name='receipt')
    receipt_number = models.CharField(max_length=100, unique=True)
    invoice_number = models.CharField(max_length=100, unique=True)
    
    # Billing details
    billing_name = models.CharField(max_length=255)
    billing_email = models.EmailField()
    billing_phone = models.CharField(max_length=20, blank=True, null=True)
    billing_address = models.TextField(blank=True, null=True)
    
    # Items
    items = models.JSONField(default=list, help_text="List of items purchased")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    
    # File
    pdf_file = models.FileField(upload_to='payments/invoices/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.transaction.transaction_id}"