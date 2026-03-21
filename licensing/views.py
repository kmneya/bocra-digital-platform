from django.shortcuts import render, get_object_or_404,redirect
from .models import LicenseApplication,AircraftRadioLicense
from django.contrib.auth.decorators import login_required
from .forms import LicenseForm


@login_required
def apply_license(request):
    if request.method == "POST":
        license_type = request.POST.get("license_type")

        if license_type == "aircraft_radio":
            return redirect('aircraft_license_form')

    return render(request, 'licensing/apply.html')

@login_required
def aircraft_license_form(request):
    if request.method == "POST":

        license_app = LicenseApplication.objects.create(
            business_name=request.POST.get("name"),
            user=request.user,
            license_type='aircraft_radio',
            status='pending'
        )
        AircraftRadioLicense.objects.create(
            user=request.user,
            name=request.POST.get("name"),
            nationality=request.POST.get("nationality"),
            email=request.POST.get("email"),
            station_name=request.POST.get("station_name"),
            city=request.POST.get("city"),
            equipment_type=request.POST.get("equipment_type"),
            model=request.POST.get("model"),
        )

        return redirect('license_list')

    return render(request, 'licensing/aircraft_form.html')

@login_required
def license_list(request):
    applications = LicenseApplication.objects.filter(user=request.user)
    return render(request, 'licensing/list.html', {"applications": applications})


@login_required
def license_detail(request, pk):
    application = get_object_or_404(LicenseApplication, id=pk, user=request.user)
    return render(request, 'licensing/detail.html', {"application": application})