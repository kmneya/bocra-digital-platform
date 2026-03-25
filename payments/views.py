from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from users.decorators import citizen_required, officer_required
from licensing.models import LicenseApplication
from .models import PaymentTransaction, PaymentMethod, PaymentReceipt
from .forms import PaymentForm, PaymentConfirmationForm
import uuid
import json
from django.db import models

@login_required
@citizen_required
def initiate_payment(request, license_id):
    """Initiate payment for a license application"""
    license_app = get_object_or_404(LicenseApplication, id=license_id, user=request.user)
    
    # Check if payment already exists
    existing_payment = PaymentTransaction.objects.filter(
        license_application=license_app,
        status__in=['pending', 'processing', 'completed']
    ).first()
    
    if existing_payment:
        if existing_payment.status == 'completed':
            messages.info(request, f'Payment already completed for this application.')
            return redirect('license_detail', pk=license_app.id)
        else:
            messages.warning(request, f'You already have a pending payment. Please complete it or contact support.')
            return redirect('payment_status', payment_id=existing_payment.id)
    
    # Calculate license fee (example logic)
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
    
    amount = license_fees.get(license_app.license_type, 500.00)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = request.user
            payment.license_application = license_app
            payment.amount = amount
            payment.status = 'pending'
            payment.save()
            
            messages.info(request, f'Payment initiated. Please complete payment using the instructions below.')
            return redirect('payment_checkout', payment_id=payment.id)
    else:
        initial_data = {
            'amount': amount,
            'payment_type': 'license_fee',
            'description': f'License Application Fee - {license_app.get_license_type_display()}',
        }
        form = PaymentForm(initial=initial_data)
    
    context = {
        'license_app': license_app,
        'form': form,
        'amount': amount,
    }
    
    return render(request, 'payments/initiate.html', context)


@login_required
@citizen_required
def payment_checkout(request, payment_id):
    """Simulated payment checkout page"""
    payment = get_object_or_404(PaymentTransaction, id=payment_id, user=request.user)
    
    if payment.status == 'completed':
        messages.info(request, 'This payment has already been completed.')
        return redirect('license_list')
    
    # Simulate payment gateway options
    payment_methods = {
        'mobile_money': {
            'name': 'Mobile Money',
            'instructions': 'Dial *131# and follow prompts to send payment to BOCRA',
            'reference': payment.transaction_id,
            'icon': 'fas fa-mobile-alt'
        },
        'credit_card': {
            'name': 'Credit/Debit Card',
            'instructions': 'Enter your card details below (simulated)',
            'icon': 'fas fa-credit-card'
        },
        'bank_transfer': {
            'name': 'Bank Transfer',
            'instructions': f'Transfer to BOCRA Account:\nAccount: 1234567890\nBank: Bank of Botswana\nReference: {payment.transaction_id}',
            'icon': 'fas fa-university'
        },
    }
    
    selected_method = payment_methods.get(payment.payment_method.code if payment.payment_method else 'mobile_money', payment_methods['mobile_money'])
    
    if request.method == 'POST':
        # Simulate payment processing
        payment.status = 'processing'
        payment.save()
        
        # Simulate gateway response
        payment.gateway_response = {
            'status': 'success',
            'reference': str(uuid.uuid4()),
            'timestamp': str(timezone.now()),
            'simulated': True
        }
        payment.gateway_reference = payment.gateway_response['reference']
        payment.paid_at = timezone.now()
        payment.status = 'completed'
        payment.save()
        
        # Create receipt
        PaymentReceipt.objects.create(
            transaction=payment,
            receipt_number=f"RCP-{payment.id}-{payment.transaction_id[-6:]}",
            invoice_number=f"INV-{payment.id}-{payment.transaction_id[-6:]}",
            billing_name=request.user.get_full_name() or request.user.username,
            billing_email=request.user.email,
            billing_phone=request.user.phone_number if hasattr(request.user, 'phone_number') else '',
            billing_address='Not provided',
            items=[{
                'description': payment.description,
                'amount': float(payment.amount),
                'quantity': 1
            }],
            subtotal=payment.amount,
            tax=0,
            total=payment.amount
        )
        
        # Update license application status to under review
        if payment.license_application:
            payment.license_application.status = 'under_review'
            payment.license_application.save()
        
        # 🔥 Set success message and redirect to license list
        messages.success(
            request, 
            f'✓ Payment of P{payment.amount} for {payment.license_application.get_license_type_display()} was successful!'
        )
        return redirect('license_list')
    
    context = {
        'payment': payment,
        'payment_method': selected_method,
        'amount': payment.amount,
        'transaction_id': payment.transaction_id,
    }
    
    return render(request, 'payments/checkout.html', context)

@login_required
def payment_success(request, payment_id):
    """Payment success page - redirects to license list"""
    payment = get_object_or_404(PaymentTransaction, id=payment_id, user=request.user)
    
    messages.success(
        request, 
        f'✓ Payment of P{payment.amount} for {payment.license_application.get_license_type_display()} was successful!'
    )
    
    return redirect('license_list')

@login_required
def payment_status(request, payment_id):
    """View payment status"""
    payment = get_object_or_404(PaymentTransaction, id=payment_id)
    
    # Security: Only owner or officer can view
    if request.user.role != 'officer' and payment.user != request.user:
        messages.error(request, 'You do not have permission to view this payment.')
        return redirect('dashboard_redirect')
    
    context = {
        'payment': payment,
        'can_verify': request.user.role == 'officer',
    }
    
    return render(request, 'payments/status.html', context)


@login_required
@officer_required
def payment_list(request):
    """Officer dashboard for payments monitoring"""
    payments = PaymentTransaction.objects.all().order_by('-created_at')
    
    # Statistics
    total_paid = payments.filter(status='completed').aggregate(
        total=models.Sum('amount')
    )['total'] or 0
    
    pending_count = payments.filter(status='pending').count()
    processing_count = payments.filter(status='processing').count()
    completed_count = payments.filter(status='completed').count()
    
    # Group by license type
    payments_by_type = payments.values('payment_type').annotate(
        count=models.Count('id'),
        total=models.Sum('amount')
    )
    
    context = {
        'payments': payments,
        'total_paid': total_paid,
        'pending_count': pending_count,
        'processing_count': processing_count,
        'completed_count': completed_count,
        'payments_by_type': payments_by_type,
    }
    
    return render(request, 'dashboard/payment_reports.html', context)


@login_required
@officer_required
def verify_payment(request, payment_id):
    """Officer verification of payment"""
    payment = get_object_or_404(PaymentTransaction, id=payment_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'verify':
            payment.status = 'completed'
            payment.paid_at = timezone.now()
            messages.success(request, f'Payment {payment.transaction_id} has been verified.')
            
            # Update license application if linked
            if payment.license_application:
                payment.license_application.status = 'under_review'
                payment.license_application.save()
        
        elif action == 'reject':
            payment.status = 'failed'
            messages.warning(request, f'Payment {payment.transaction_id} has been rejected.')
        
        payment.gateway_response = {
            'verified_by': request.user.username,
            'verified_at': str(timezone.now()),
            'notes': notes,
            'action': action
        }
        payment.save()
        
        return redirect('payment_list')
    
    context = {
        'payment': payment,
    }
    
    return render(request, 'payments/verify.html', context)