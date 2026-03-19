from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def citizen_dashboard(request):
    return render(request, 'dashboard/citizen.html')


@login_required
def officer_dashboard(request):
    return render(request, 'dashboard/officer.html')


@login_required
def admin_dashboard(request):
    return render(request, 'dashboard/admin.html')
