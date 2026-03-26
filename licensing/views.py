from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.decorators import citizen_required, officer_required
from .models import LicenseApplication, AircraftRadioLicense, CellularLicense
from .forms import CellularLicenseForm
from django.utils import timezone
from django.db.models import Q, Count, Sum
from payments.models import PaymentTransaction


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
        return redirect('initiate_payment', license_id=license_app.id)

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
        return redirect('initiate_payment', license_id=license_app.id)

    return render(request, 'licensing/cellular_form.html')




@login_required
def license_list(request):

    # Clear message after showing it once
    if 'submitted' in request.GET:
        messages.get_messages(request).used = True
    
    """List all licenses for the current user"""
    if request.user.role == 'officer':
        licenses = LicenseApplication.objects.all()
    else:
        licenses = LicenseApplication.objects.filter(user=request.user)
    
    # Calculate payment statistics
    paid_count = 0
    pending_payment_count = 0
    under_review_count = 0
    approved_count = 0
    rejected_count = 0
    
    for license in licenses:
        payment = license.payments.first() if hasattr(license, 'payments') else None
        
        if payment and payment.status == 'completed':
            paid_count += 1
        elif payment and payment.status in ['pending', 'processing']:
            pending_payment_count += 1
        elif not payment:
            pending_payment_count += 1
        
        # Application status counts
        if license.status == 'under_review':
            under_review_count += 1
        elif license.status == 'approved':
            approved_count += 1
        elif license.status == 'rejected':
            rejected_count += 1
    
    context = {
        'licenses': licenses,
        'paid_count': paid_count,
        'pending_payment_count': pending_payment_count,
        'under_review_count': under_review_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    
    return render(request, 'licensing/list.html', context)

@login_required
def license_detail(request, pk):
    """View a single license application"""
    license_app = get_object_or_404(LicenseApplication, id=pk)
    
    # Check permissions
    if request.user.role != 'officer' and license_app.user != request.user:
        messages.error(request, "You don't have permission to view this application.")
        return redirect('license_list')
    
    # Get payment info
    payment = None
    if hasattr(license_app, 'payments'):
        payment = license_app.payments.first()
    
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
    
    # Determine what actions are available to the user
    show_payment_button = False
    show_track_payment = False
    show_view_receipt = False
    payment_message = None
    
    if request.user.role == 'citizen':
        if payment:
            if payment.status == 'completed':
                show_view_receipt = True
                payment_message = 'Payment completed successfully!'
            elif payment.status == 'pending':
                show_track_payment = True
                payment_message = 'Your payment is being processed.'
            elif payment.status == 'failed':
                show_payment_button = True
                payment_message = 'Your payment failed. Please try again.'
        else:
            # No payment record exists
            if license_app.status == 'submitted':
                show_payment_button = True
                payment_message = 'Payment required to process your application.'
            elif license_app.status == 'approved':
                payment_message = 'Your license has been approved!'
            elif license_app.status == 'rejected':
                payment_message = 'Your application was rejected.'
            elif license_app.status == 'under_review':
                payment_message = 'Your application is under review.'
    
    context = {
        'application': license_app,
        'specific_details': specific_details,
        'payment': payment,
        'show_payment_button': show_payment_button,
        'show_track_payment': show_track_payment,
        'show_view_receipt': show_view_receipt,
        'payment_message': payment_message,
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

@login_required
@officer_required
def officer_license_list(request):
    """Officer view for all license applications"""
    # Get all applications with payment info
    applications = LicenseApplication.objects.all().order_by('-created_at')
    
    # Add payment info to each application
    for app in applications:
        payment = PaymentTransaction.objects.filter(license_application=app).first()
        app.has_payment = payment is not None
        app.payment_status = payment.status if payment else 'not_paid'
        app.payment_amount = payment.amount if payment else None
    
    # Statistics
    total_applications = applications.count()
    pending_review = applications.filter(status='submitted').count()
    under_review = applications.filter(status='under_review').count()
    approved = applications.filter(status='approved').count()
    rejected = applications.filter(status='rejected').count()
    
    # Get applications by license type
    by_type = applications.values('license_type').annotate(count=Count('id'))
    
    context = {
        'applications': applications,
        'total_applications': total_applications,
        'pending': pending_review,
        'under_review': under_review,
        'approved': approved,
        'rejected': rejected,
        'by_type': by_type,
    }
    
    return render(request, 'licensing/officer_list.html', context)


@login_required
@officer_required
def officer_license_detail(request, pk):
    """Officer view for a single license application"""
    application = get_object_or_404(LicenseApplication, id=pk)
    
    # Get payment info
    payment = PaymentTransaction.objects.filter(license_application=application).first()
    
    # Get specific license details based on type
    specific_details = None
    if application.license_type == 'aircraft_radio':
        try:
            specific_details = AircraftRadioLicense.objects.get(application=application)
        except AircraftRadioLicense.DoesNotExist:
            pass
    elif application.license_type == 'cellular_details':
        try:
            specific_details = CellularLicense.objects.get(application=application)
        except CellularLicense.DoesNotExist:
            pass
    
    context = {
        'application': application,
        'payment': payment,
        'specific_details': specific_details,
    }
    
    return render(request, 'licensing/officer_detail.html', context)


@login_required
@officer_required
def officer_license_action(request, pk):
    """Process approve/reject action on license"""
    application = get_object_or_404(LicenseApplication, id=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            application.status = 'approved'
            application.reviewed_at = timezone.now()
            application.reviewed_by = request.user
            application.review_notes = notes
            application.save()
            
            messages.success(
                request, 
                f'License application #{application.id} for {application.business_name} has been APPROVED.'
            )
            
        elif action == 'reject':
            application.status = 'rejected'
            application.reviewed_at = timezone.now()
            application.reviewed_by = request.user
            application.review_notes = notes
            application.save()
            
            messages.warning(
                request, 
                f'License application #{application.id} for {application.business_name} has been REJECTED.'
            )
        
        elif action == 'request_info':
            application.status = 'additional_info'
            application.review_notes = notes
            application.save()
            
            messages.info(
                request, 
                f'Additional information requested for application #{application.id}.'
            )
        
        return redirect('officer_license_list')
    
    return redirect('officer_license_detail', pk=pk)