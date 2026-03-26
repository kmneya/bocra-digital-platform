from django.contrib import admin
from .models import PaymentMethod, PaymentTransaction, PaymentReceipt

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'status', 'payment_type', 'created_at')
    list_filter = ('status', 'payment_type', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'user__username', 'gateway_reference')
    readonly_fields = ('transaction_id', 'reference_number', 'created_at', 'updated_at')
    fieldsets = (
        ('Transaction Information', {
            'fields': ('transaction_id', 'reference_number', 'user', 'license_application')
        }),
        ('Payment Details', {
            'fields': ('payment_type', 'payment_method', 'amount', 'currency', 'description')
        }),
        ('Status', {
            'fields': ('status', 'paid_at')
        }),
        ('Gateway Information', {
            'fields': ('payment_gateway', 'gateway_reference', 'gateway_response'),
            'classes': ('collapse',)
        }),
        ('Receipt', {
            'fields': ('receipt_number', 'receipt_file'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'transaction', 'billing_name', 'total', 'created_at')
    search_fields = ('receipt_number', 'invoice_number', 'billing_name', 'billing_email')
    readonly_fields = ('created_at',)