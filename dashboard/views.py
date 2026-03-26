from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Count, Avg, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import render, redirect
from django.utils import timezone
from complaints.models import Complaint
from licensing.models import LicenseApplication
from monitoring.models import TelecomProvider, NetworkQualityMetrics, NetworkIncident
from payments.models import PaymentTransaction
from users.models import User

@login_required
def redirect_dashboard(request):
    """Redirect to appropriate dashboard based on role"""
    user = request.user
    
    # Debug: Print user info
    print(f"Redirecting user: {user.username}")
    print(f"Role: {user.role}")
    print(f"Is Superuser: {user.is_superuser}")
    
    # Check superuser first
    if user.is_superuser:
        print("Redirecting to admin_dashboard (superuser)")
        return redirect('admin_dashboard')
    elif user.role == 'admin':
        print("Redirecting to admin_dashboard (admin role)")
        return redirect('admin_dashboard')
    elif user.role == 'officer':
        print("Redirecting to officer_dashboard")
        return redirect('officer_dashboard')
    else:
        print("Redirecting to citizen_dashboard")
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
    """Admin dashboard - ADMIN ONLY"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('citizen_dashboard')
    
    # Get current date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # ========== COMPLAINTS STATISTICS ==========
    total_complaints = Complaint.objects.count()
    resolved_complaints = Complaint.objects.filter(status='resolved').count()
    pending_complaints = Complaint.objects.filter(status='pending').count()
    under_review = Complaint.objects.filter(status='investigating').count()
    
    # Resolution rate
    resolution_rate = 0
    if total_complaints > 0:
        resolution_rate = round((resolved_complaints / total_complaints) * 100, 1)
    
    # Complaints by status (for chart)
    complaints_by_status = Complaint.objects.values('status').annotate(
        total=Count('id')
    )
    
    # Complaints over time (last 30 days)
    complaints_trend = Complaint.objects.filter(
        created_at__gte=month_ago
    ).extra({'date': "date(created_at)"}).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Average resolution time
    avg_resolution = Complaint.objects.filter(
        status='resolved',
        resolved_at__isnull=False
    ).annotate(
        resolution_time=models.ExpressionWrapper(
            models.F('resolved_at') - models.F('created_at'),
            output_field=models.DurationField()
        )
    ).aggregate(avg=models.Avg('resolution_time'))
    
    avg_hours = 0
    if avg_resolution['avg']:
        avg_hours = int(avg_resolution['avg'].total_seconds() / 3600)
    
    # ========== LICENSING STATISTICS ==========
    total_licenses = LicenseApplication.objects.count()
    approved_licenses = LicenseApplication.objects.filter(status='approved').count()
    pending_licenses = LicenseApplication.objects.filter(status='pending').count()
    rejected_licenses = LicenseApplication.objects.filter(status='rejected').count()
    
    # Licenses by type
    licenses_by_type = LicenseApplication.objects.values('license_type').annotate(
        total=Count('id')
    )
    
    # ========== PAYMENT STATISTICS ==========
    total_revenue = PaymentTransaction.objects.filter(
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_revenue = PaymentTransaction.objects.filter(
        status='completed',
        paid_at__date__gte=month_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    weekly_revenue = PaymentTransaction.objects.filter(
        status='completed',
        paid_at__date__gte=week_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    pending_payments = PaymentTransaction.objects.filter(status='pending').count()
    
    # ========== OFFICER PERFORMANCE ==========
    officers = User.objects.filter(role='officer')
    officer_performance = []
    
    for officer in officers:
        assigned_complaints = Complaint.objects.filter(assigned_to=officer).count()
        resolved_by_officer = Complaint.objects.filter(
            assigned_to=officer,
            status='resolved'
        ).count()
        
        officer_performance.append({
            'name': officer.get_full_name() or officer.username,
            'assigned': assigned_complaints,
            'resolved': resolved_by_officer,
            'resolution_rate': round((resolved_by_officer / assigned_complaints * 100), 1) if assigned_complaints > 0 else 0
        })
    
    # ========== NETWORK MONITORING ==========
    active_incidents = NetworkIncident.objects.filter(is_resolved=False).count()
    
    # ========== SYSTEM CONFIGURATION ==========
    license_fees = {
        'aircraft_radio': 500.00,
        'cellular_details': 2500.00,
        'broadcasting_lis': 1500.00,
        'vans_lis': 1000.00,
        'point_to_to_lis': 800.00,
        'satellite_service_lis': 1200.00,
        'amateur_rad_lis': 300.00,
        'citizen_band_rad_lis': 250.00,
    }
    
    # ========== SLA COMPLIANCE ==========
    # Calculate complaints resolved within SLA (48 hours default)
    sla_compliant = 0
    for complaint in Complaint.objects.filter(status='resolved'):
        if complaint.resolved_at and complaint.created_at:
            resolution_hours = (complaint.resolved_at - complaint.created_at).total_seconds() / 3600
            if resolution_hours <= 48:
                sla_compliant += 1
    
    sla_compliance = 0
    if resolved_complaints > 0:
        sla_compliance = round((sla_compliant / resolved_complaints) * 100, 1)
    
    context = {
        # Complaints
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'pending_complaints': pending_complaints,
        'under_review': under_review,
        'resolution_rate': resolution_rate,
        'complaints_by_status': complaints_by_status,
        'complaints_trend': list(complaints_trend),
        'avg_resolution_time': avg_hours,
        
        # Licensing
        'total_licenses': total_licenses,
        'approved_licenses': approved_licenses,
        'pending_licenses': pending_licenses,
        'rejected_licenses': rejected_licenses,
        'licenses_by_type': licenses_by_type,
        
        # Payments
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'weekly_revenue': weekly_revenue,
        'pending_payments': pending_payments,
        
        # Officer Performance
        'officer_performance': officer_performance,
        
        # System
        'active_incidents': active_incidents,
        'license_fees': license_fees,
        'sla_compliance': sla_compliance,
    }
    
    return render(request, 'dashboard/admin.html', context)

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


@login_required
def admin_users(request):
    """Admin view to manage users"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('citizen_dashboard')
    
    users = User.objects.all().order_by('-date_joined')
    
    context = {
        'users': users,
        'total_users': users.count(),
        'officers': users.filter(role='officer').count(),
        'citizens': users.filter(role='citizen').count(),
        'admins': users.filter(is_superuser=True).count(),
    }
    
    return render(request, 'dashboard/admin_users.html', context)


@login_required
def admin_create_user(request):
    """Admin view to create new users"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('citizen_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.role = role
            user.save()
            
            messages.success(request, f'User {username} created successfully as {role}.')
            return redirect('admin_users')
    
    return render(request, 'dashboard/admin_create_user.html')