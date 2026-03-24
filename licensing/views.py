from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.decorators import citizen_required, officer_required
from .models import LicenseApplication, AircraftRadioLicense, CellularLicense
from .forms import CellularLicenseForm

@login_required
@citizen_required
def apply_license(request):
    """Select license type to apply for"""
    if request.method == "POST":
        license_type = request.POST.get("license_type")
        business_name = request.POST.get('business_name')
        details = request.POST.get('details')

        if license_type == "aircraft_radio":
            # Store common fields in session for aircraft form
            request.session['temp_business_name'] = business_name
            request.session['temp_details'] = details
            return redirect('aircraft_license_form')
        
        elif license_type == 'cellular_details':
            # Store common fields in session for cellular form
            request.session['temp_business_name'] = business_name
            request.session['temp_details'] = details
            return redirect('cellular_license_form')

    return render(request, 'licensing/apply.html')


@login_required
def aircraft_license_form(request):
    """Aircraft Radio License specific form"""
    if request.method == "POST":
        # Create the main license application
        license_app = LicenseApplication.objects.create(
            business_name=request.session.get('temp_business_name', request.POST.get("name")),
            details=request.session.get('temp_details', 'Aircraft Radio License Application'),
            user=request.user,
            license_type='aircraft_radio',
            status='submitted'
        )
        
        # Create the detailed aircraft license
        AircraftRadioLicense.objects.create(
            user=request.user,
            application=license_app,  # Link to main application
            client_type=request.POST.get("client_type", "person") or "",
            name=request.POST.get("name") or "",
            nationality=request.POST.get("nationality")or "",
            company_reg_number=request.POST.get("company_reg_number", "")or "",
            email=request.POST.get("email")or "",
            phone=request.POST.get("phone") or "",
            station_name=request.POST.get("station_name") or "",
            city=request.POST.get("city") or "",
            latitude=request.POST.get("latitude", "") or "",
            longitude=request.POST.get("longitude", "") or "",
            equipment_type=request.POST.get("equipment_type") or "",
            make=request.POST.get("make") or "",
            model=request.POST.get("model") or "",
            serial_number=request.POST.get("serial_number", "") or "",
        )
        
        # Clear session data
        request.session.pop('temp_business_name', None)
        request.session.pop('temp_details', None)
        
        messages.success(request, f'Aircraft Radio License application submitted successfully!')
        return redirect('license_list')

    return render(request, 'licensing/aircraft_form.html')


@login_required
def cellular_license_form(request):
    """Cellular License specific form"""
    if request.method == "POST":
        # Create the main license application
        license_app = LicenseApplication.objects.create(
            business_name=request.session.get('temp_business_name', request.POST.get("site_name")),
            details=request.session.get('temp_details', 'Cellular License Application'),
            user=request.user,
            license_type='cellular_details',
            status='submitted'
        )
        
        # Create the detailed cellular license
        CellularLicense.objects.create(
            user=request.user,
            application=license_app,  # Link to main application
            site_name=request.POST.get("site_name"),
            site_location=request.POST.get("site_location"),
            equipment_type=request.POST.get("equipment_type"),
            frequency_band=request.POST.get("frequency_band"),
            service_type=request.POST.get("service_type"),
            coverage_area=request.POST.get("coverage_area", ""),
        )
        
        # Clear session data
        request.session.pop('temp_business_name', None)
        request.session.pop('temp_details', None)
        
        messages.success(request, f'Cellular License application submitted successfully!')
        return redirect('license_list')

    return render(request, 'licensing/cellular_form.html')


@login_required
def license_list(request):
    """List all licenses for the current user"""
    if request.user.role == 'officer':
        licenses = LicenseApplication.objects.all()
    else:
        licenses = LicenseApplication.objects.filter(user=request.user)
    
    # Debug: Print to console
    print(f"User: {request.user.username}")
    print(f"Role: {request.user.role}")
    print(f"License count: {licenses.count()}")
    for license in licenses:
        print(f"License: {license.business_name} - {license.license_type}")
    
    return render(request, 'licensing/list.html', {'licenses': licenses})


@login_required
def license_detail(request, pk):
    """View a single license application with its specific details"""
    license_app = get_object_or_404(LicenseApplication, id=pk)
    
    # Check permissions
    if request.user.role != 'officer' and license_app.user != request.user:
        messages.error(request, "You don't have permission to view this application.")
        return redirect('license_list')
    
    # Get the specific license details based on type
    specific_details = None
    if license_app.license_type == 'aircraft_radio':
        try:
            specific_details = AircraftRadioLicense.objects.get(application=license_app)
        except AircraftRadioLicense.DoesNotExist:
            pass
    elif license_app.license_type == 'cellular_details':
        try:
            specific_details = CellularLicense.objects.get(application=license_app)
        except CellularLicense.DoesNotExist:
            pass
    
    context = {
        'application': license_app,
        'specific_details': specific_details,
    }
    
    return render(request, 'licensing/detail.html', context)


@login_required
@officer_required
def review_license(request, pk):
    """Review and approve/reject license - OFFICERS ONLY"""
    license_app = get_object_or_404(LicenseApplication, id=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            license_app.status = 'approved'
            messages.success(request, f'License {license_app.business_name} has been approved.')
        elif action == 'reject':
            license_app.status = 'rejected'
            messages.warning(request, f'License {license_app.business_name} has been rejected.')
        
        license_app.reviewed_by = request.user
        license_app.review_notes = notes
        license_app.save()
        
        return redirect('license_list')
    
    return render(request, 'licensing/review.html', {'application': license_app})