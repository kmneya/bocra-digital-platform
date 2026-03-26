from django.contrib import admin
from .models import Complaint, ComplaintUpdate

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ( 'name', 'email', 'telephone')
    readonly_fields = ( 'created_at', 'updated_at')
    fieldsets = (
        ('Complainant Information', {
            'fields': ('name', 'company', 'telephone', 'email')
        }),
        ('Complaint Details', {
            'fields': ('category', 'complaint_text')
        }),
        ('Tracking', {
            'fields': ( 'status', 'assigned_to')
        }),
        ('Resolution', {
            'fields': ('investigation_notes', 'resolution_summary', 'resolved_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ComplaintUpdate)
class ComplaintUpdateAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'updated_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('comment',)