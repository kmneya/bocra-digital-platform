from django.urls import path
from . import views

urlpatterns = [
    path('citizen/', views.citizen_dashboard, name='citizen_dashboard'),
    path('officer/', views.officer_dashboard, name='officer_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    # This is the root dashboard URL
    path('', views.redirect_dashboard, name='dashboard_redirect'),

    # Complaints Analytics
    path('complaints/analytics/', views.complaints_analytics, name='complaints_analytics'),
    path('complaints/pending/', views.pending_complaints, name='pending_complaints'),
    path('complaints/sla/', views.sla_report, name='sla_report'),
    
    # Licensing Analytics
    path('licenses/analytics/', views.licensing_analytics, name='licensing_analytics'),
    path('licenses/pending/', views.pending_licenses_view, name='pending_licenses'),
    path('licenses/approved/', views.approved_licenses_view, name='approved_licenses'),
    
    # Network Monitoring
    path('monitoring/', views.network_monitoring, name='network_monitoring'),
    path('monitoring/spectrum/', views.spectrum_analysis, name='spectrum_analysis'),
    path('monitoring/incidents/', views.incident_reports, name='incident_reports'),
    path('monitoring/regional/', views.regional_qos, name='regional_qos'),
    
    # Reports
    path('reports/generate/', views.generate_reports, name='generate_reports'),
    path('reports/export/', views.export_data, name='export_data'),
    path('reports/annual/', views.annual_report, name='annual_report'),
    
    # Settings
    path('settings/', views.officer_settings, name='officer_settings'),
    path('settings/notifications/', views.notification_settings, name='notification_settings'),
]