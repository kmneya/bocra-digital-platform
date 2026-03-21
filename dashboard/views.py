from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from complaints.models import Complaint
from licensing.models import LicenseApplication

@login_required
def citizen_dashboard(request):
    complaints = Complaint.objects.filter(user=request.user)
    licenses = LicenseApplication.objects.filter(user=request.user)

    return render(request, 'dashboard/citizen.html', {
        'complaints': complaints,
        'licenses': licenses
    })


@login_required
def officer_dashboard(request):
    complaints = Complaint.objects.filter(assigned_to=request.user)

    return render(request, 'dashboard/officer.html', {
        "complaints": complaints
    })


@login_required
def admin_dashboard(request):
    return render(request, 'dashboard/admin.html')
