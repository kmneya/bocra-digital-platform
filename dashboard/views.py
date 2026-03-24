from django.db import models
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
    complaints = Complaint.objects.filter(user=request.user)
    
    context = {
        "complaints": complaints,
        "resolved_count": complaints.filter(status='resolved').count(),
        "pending_count": complaints.filter(status='pending').count(),
    }
    
    return render(request, 'dashboard/citizen.html', context)

@login_required
def officer_dashboard(request):
    # 🔒 Security: Only officers can access this
    if request.user.role != 'officer':
        return redirect('citizen_dashboard')
    
    # 📊 Complaint stats
    total_complaints = Complaint.objects.count()
    resolved = Complaint.objects.filter(status='resolved').count()
    pending = Complaint.objects.filter(status='pending').count()
    in_progress = Complaint.objects.filter(status='in_progress').count()
    
    # Calculate resolution rate
    resolution_rate = 0
    if total_complaints > 0:
        resolution_rate = (resolved / total_complaints) * 100
    
    # 📊 Complaints by category
    complaints_by_category = Complaint.objects.values('category').annotate(
        total=Count('id')
    ).order_by('-total')
    
    # 📊 Complaints by status
    complaints_by_status = Complaint.objects.values('status').annotate(
        total=Count('id')
    )
    
    # 📊 Complaints trend (last 30 days)
    last_30_days = timezone.now() - timedelta(days=30)
    complaints_trend = Complaint.objects.filter(
        created_at__gte=last_30_days
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # 📄 Licensing stats
    total_licenses = LicenseApplication.objects.count()
    pending_licenses = LicenseApplication.objects.filter(status='pending').count()
    approved_licenses = LicenseApplication.objects.filter(status='approved').count()
    
    # 📋 Pending complaints list
    pending_complaints_list = Complaint.objects.filter(
        status='pending'
    ).order_by('-created_at')[:10]
    
    # 📋 Pending licenses list
    pending_licenses_list = LicenseApplication.objects.filter(
        status='pending'
    ).order_by('-created_at')[:10]
    
    # 🔥 SLA Analytics
    sla_compliant = Complaint.objects.filter(
        status='resolved',
        resolved_at__lte=models.F('created_at') + models.F('sla_hours') * timedelta(hours=1)
    ).count()
    
    sla_compliance = 0
    if resolved > 0:
        sla_compliance = (sla_compliant / resolved) * 100
    
    # Average resolution time (in hours)
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
    
    # SLA breached count
    sla_breached = Complaint.objects.filter(
        status='pending',
        created_at__lte=timezone.now() - models.F('sla_hours') * timedelta(hours=1)
    ).count()
    
    # Weekly complaints
    week_ago = timezone.now() - timedelta(days=7)
    weekly_complaints = Complaint.objects.filter(created_at__gte=week_ago).count()
    
    # Most common category
    top_category_data = Complaint.objects.values('category').annotate(
        total=Count('id')
    ).order_by('-total').first()
    top_category = top_category_data['category'] if top_category_data else 'N/A'
    
    context = {
        # KPI Cards
        'total_complaints': total_complaints,
        'resolved': resolved,
        'pending': pending,
        'in_progress': in_progress,
        'resolution_rate': round(resolution_rate, 1),
        'total_licenses': total_licenses,
        'pending_licenses': pending_licenses,
        'approved_licenses': approved_licenses,
        
        # Charts
        'complaints_by_category': complaints_by_category,
        'complaints_by_status': complaints_by_status,
        'complaints_trend': list(complaints_trend),
        
        # Actionable lists
        'pending_complaints_list': pending_complaints_list,
        'pending_licenses_list': pending_licenses_list,
        
        # SLA Analytics
        'sla_compliance': round(sla_compliance, 1),
        'avg_resolution_time': avg_hours,
        'sla_breached': sla_breached,
        'weekly_complaints': weekly_complaints,
        'top_category': top_category,
    }
    
    return render(request, 'dashboard/officer.html', context)

@login_required
def admin_dashboard(request):
    return render(request, 'dashboard/admin.html')
