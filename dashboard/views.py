from django.db import models
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from complaints.models import Complaint
from licensing.models import LicenseApplication
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta


@login_required
def redirect_dashboard(request):
    """Redirect to the appropriate dashboard based on user role"""
    if request.user.role == 'officer':
        return redirect('officer_dashboard')
    elif request.user.role == 'admin':
        return redirect('admin_dashboard')
    else:
        return redirect('citizen_dashboard')

@login_required
def citizen_dashboard(request):
    if request.user.role != 'citizen':
        return redirect('officer_dashboard')
    messages.get_messages(request).used = True
    
    complaints = Complaint.objects.filter(user=request.user)
    
    context = {
        "complaints": complaints,
        "resolved_count": complaints.filter(status='resolved').count(),
        "pending_count": complaints.filter(status='pending').count(),
    }
    
    return render(request, 'dashboard/citizen.html', context)

@login_required
def officer_dashboard(request):
    """Officer dashboard - OFFICERS ONLY"""
    # Redirect if not officer
    if request.user.role != 'officer':
        if request.user.role == 'citizen':
            return redirect('citizen_dashboard')
        elif request.user.role == 'admin':
            return redirect('admin_dashboard')
    
    # Get provider data for sidebar
    from monitoring.models import TelecomProvider, NetworkQualityMetrics
    providers = TelecomProvider.objects.all()
    provider_data = []
    for provider in providers:
        latest_metrics = NetworkQualityMetrics.objects.filter(
            provider=provider
        ).order_by('-date').first()
        provider_data.append({
            'name': provider.name,
            'color': provider.color,
            'avg_throughput': latest_metrics.avg_throughput if latest_metrics else 45,
            'avg_latency': latest_metrics.latency if latest_metrics else 35,
            'uptime': latest_metrics.uptime_percentage if latest_metrics else 99.5,
        })
    
    # Your existing stats...
    total_complaints = Complaint.objects.count()
    resolved = Complaint.objects.filter(status='resolved').count()
    pending = Complaint.objects.filter(status='pending').count()
    
    resolution_rate = 0
    if total_complaints > 0:
        resolution_rate = (resolved / total_complaints) * 100
    
    complaints_by_category = Complaint.objects.values('category').annotate(
        total=Count('id')
    )
    
    complaints_by_status = Complaint.objects.values('status').annotate(
        total=Count('id')
    )
    
    pending_complaints_list = Complaint.objects.filter(
        status='pending'
    ).order_by('-created_at')[:10]
    
    total_licenses = LicenseApplication.objects.count()
    pending_licenses = LicenseApplication.objects.filter(status='pending').count()
    approved_licenses = LicenseApplication.objects.filter(status='approved').count()
    
    # Add sidebar counts
    active_incidents = NetworkIncident.objects.filter(is_resolved=False).count()
    
    context = {
        # Your existing context...
        'total_complaints': total_complaints,
        'resolved': resolved,
        'pending': pending,
        'resolution_rate': round(resolution_rate, 1),
        'complaints_by_category': complaints_by_category,
        'complaints_by_status': complaints_by_status,
        'pending_complaints_list': pending_complaints_list,
        'total_licenses': total_licenses,
        'pending_licenses': pending_licenses,
        'approved_licenses': approved_licenses,
        
        # Sidebar data
        'providers': provider_data,
        'active_incidents': active_incidents,
        'weekly_complaints': Complaint.objects.filter(created_at__gte=timezone.now() - timedelta(days=7)).count(),
        'sla_compliance': 95,  # Calculate from your SLA data
        'avg_resolution_time': 48,
        'sla_breached': 3,
        'top_category': 'Internet Service',
    }
    
    return render(request, 'dashboard/officer.html', context)

@login_required
def admin_dashboard(request):
    return render(request, 'dashboard/admin.html')


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from complaints.models import Complaint
from licensing.models import LicenseApplication
from monitoring.models import TelecomProvider, NetworkQualityMetrics, NetworkIncident
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta

# ... keep your existing citizen_dashboard, officer_dashboard, admin_dashboard, redirect_dashboard

# ========== COMPLAINTS ANALYTICS VIEWS ==========

@login_required
def complaints_analytics(request):
    """Complaints analytics page"""
    if request.user.role != 'officer':
        return redirect('citizen_dashboard')
    
    total_complaints = Complaint.objects.count()
    resolved = Complaint.objects.filter(status='resolved').count()
    pending = Complaint.objects.filter(status='pending').count()
    
    complaints_by_category = Complaint.objects.values('category').annotate(
        total=Count('id')
    )
    
    complaints_by_status = Complaint.objects.values('status').annotate(
        total=Count('id')
    )
    
    context = {
        'total_complaints': total_complaints,
        'resolved': resolved,
        'pending': pending,
        'complaints_by_category': complaints_by_category,
        'complaints_by_status': complaints_by_status,
    }
    
    return render(request, 'dashboard/complaints_analytics.html', context)


@login_required
def pending_complaints(request):
    """View all pending complaints"""
    if request.user.role != 'officer':
        return redirect('citizen_dashboard')
    
    pending_complaints = Complaint.objects.filter(status='pending').order_by('-created_at')
    
    return render(request, 'dashboard/pending_complaints.html', {'complaints': pending_complaints})


@login_required
def sla_report(request):
    """SLA compliance report"""
    if request.user.role != 'officer':
        return redirect('citizen_dashboard')
    
    total_resolved = Complaint.objects.filter(status='resolved').count()
    sla_compliant = Complaint.objects.filter(
        status='resolved'
    ).count()  # You can add actual SLA logic here
    
    sla_percentage = 0
    if total_resolved > 0:
        sla_percentage = (sla_compliant / total_resolved) * 100
    
    context = {
        'sla_compliance': round(sla_percentage, 1),
        'total_resolved': total_resolved,
        'sla_compliant': sla_compliant,
    }
    
    return render(request, 'dashboard/sla_report.html', context)


# ========== LICENSING ANALYTICS VIEWS ==========

@login_required
def licensing_analytics(request):
    """Licensing analytics page"""
    if request.user.role != 'officer':
        return redirect('citizen_dashboard')
    
    total_applications = LicenseApplication.objects.count()
    approved = LicenseApplication.objects.filter(status='approved').count()
    pending = LicenseApplication.objects.filter(status='pending').count()
    rejected = LicenseApplication.objects.filter(status='rejected').count()
    
    context = {
        'total_applications': total_applications,
        'approved': approved,
        'pending': pending,
        'rejected': rejected,
    }
    
    return render(request, 'dashboard/licensing_analytics.html', context)


@login_required
def pending_licenses_view(request):
    """View all pending license applications"""
    if request.user.role != 'officer':
        return redirect('citizen_dashboard')
    
    pending_apps = LicenseApplication.objects.filter(status='pending').order_by('-created_at')
    
    return render(request, 'dashboard/pending_licenses.html', {'applications': pending_apps})


@login_required
def approved_licenses_view(request):
    """View all approved licenses"""
    if request.user.role != 'officer':
        return redirect('citizen_dashboard')
    
    approved_apps = LicenseApplication.objects.filter(status='approved').order_by('-created_at')
    
    return render(request, 'dashboard/approved_licenses.html', {'applications': approved_apps})


# ========== NETWORK MONITORING VIEWS ==========

@login_required
def network_monitoring(request):
    """Network monitoring dashboard"""
    if request.user.role != 'officer':
        return redirect('citizen_dashboard')
    
    # Get providers
    providers = TelecomProvider.objects.all()
    
    # Get latest metrics for each provider
    provider_data = []
    for provider in providers:
        latest = NetworkQualityMetrics.objects.filter(provider=provider).order_by('-date').first()
        provider_data.append({
            'name': provider.name,
            'color': provider.color,
            'throughput': latest.avg_throughput if latest else 45,
            'latency': latest.latency if latest else 35,
            'uptime': latest.uptime_percentage if latest else 99.5,
        })
    
    context = {
        'providers': provider_data,
    }
    
    return render(request, 'dashboard/network_monitoring.html', context)


@login_required
def spectrum_analysis(request):
    """Spectrum analysis page"""
    if request.user.role != 'officer':
        return redirect('citizen_dashboard')
    
    return render(request, 'dashboard/spectrum_analysis.html')


@login_required
def incident_reports(request):
    """Incident reports page"""
    if request.user.role != 'officer':
        return redirect('citizen_dashboard')
    
    incidents = NetworkIncident.objects.all().order_by('-start_time')
    
    return render(request, 'dashboard/incident_reports.html', {'incidents': incidents})


@login_required
def regional_qos(request):
    """Regional QoS page"""
    if request.user.role != 'officer':
        return redirect('citizen_dashboard')
    
    return render(request, 'dashboard/regional_qos.html')


# ========== REPORTS VIEWS ==========

@login_required
def generate_reports(request):
    """Generate reports page"""
    if request.user.role != 'officer':
        return redirect('citizen_dashboard')
    
    return render(request, 'dashboard/generate_reports.html')


@login_required
def export_data(request):
    """Export data page"""
    if request.user.role != 'officer':
        return redirect('citizen_dashboard')
    
    return render(request, 'dashboard/export_data.html')


@login_required
def annual_report(request):
    """Annual report page"""
    if request.user.role != 'officer':
        return redirect('citizen_dashboard')
    
    return render(request, 'dashboard/annual_report.html')


# ========== SETTINGS VIEWS ==========

@login_required
def officer_settings(request):
    """Officer settings page"""
    if request.user.role != 'officer':
        return redirect('citizen_dashboard')
    
    return render(request, 'dashboard/officer_settings.html')


@login_required
def notification_settings(request):
    """Notification settings page"""
    if request.user.role != 'officer':
        return redirect('citizen_dashboard')
    
    return render(request, 'dashboard/notification_settings.html')
