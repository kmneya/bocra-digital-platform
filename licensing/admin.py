from django.contrib import admin
from .models import LicenseApplication, AircraftRadioLicense, CellularLicense

@admin.register(LicenseApplication)
class LicenseApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'business_name', 'license_type', 'status', 'user', 'created_at')
    list_filter = ('status', 'license_type', 'created_at')
    search_fields = ('business_name', 'details', 'user__username')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Application Information', {
            'fields': ('user', 'license_type', 'business_name', 'details')
        }),
        ('Status', {
            'fields': ('status', 'reviewed_by', 'review_notes', 'reviewed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(AircraftRadioLicense)
class AircraftRadioLicenseAdmin(admin.ModelAdmin):
    list_display = ('name', 'application', 'station_name', 'city', 'created_at')
    list_filter = ('city', 'created_at')
    search_fields = ('name', 'station_name', 'email', 'phone')
    fieldsets = (
        ('Applicant Details', {
            'fields': ('application', 'user', 'client_type', 'name', 'nationality', 'company_reg_number')
        }),
        ('Contact Details', {
            'fields': ('email', 'phone')
        }),
        ('Base Station', {
            'fields': ('station_name', 'city', 'latitude', 'longitude')
        }),
        ('Equipment', {
            'fields': ('equipment_type', 'make', 'model', 'serial_number')
        }),
    )

@admin.register(CellularLicense)
class CellularLicenseAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'application', 'equipment_type', 'frequency_band', 'created_at')
    list_filter = ('equipment_type', 'frequency_band', 'service_type')
    search_fields = ('site_name', 'site_location', 'equipment_type')
    fieldsets = (
        ('Site Information', {
            'fields': ('application', 'user', 'site_name', 'site_location')
        }),
        ('Equipment', {
            'fields': ('equipment_type', 'frequency_band', 'service_type')
        }),
        ('Coverage', {
            'fields': ('coverage_area',)
        }),
    )