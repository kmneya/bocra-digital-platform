from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Complaint
from .forms import ComplaintForm
from users.decorators import citizen_required, officer_required
from django.utils import timezone
from django.db.models import Q, Count
from .models import Complaint, ComplaintUpdate

@login_required
@citizen_required
def create_complaint(request):
    """Create a new complaint - CITIZENS ONLY"""
    
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            messages.success(request, f'Your complaint has been submitted successfully! Reference: {complaint.reference_number}')
            return redirect('complaint_list')
    else:
        # Pass the logged-in user to the form for auto-population
        form = ComplaintForm(user=request.user)
    
    return render(request, 'complaints/create.html', {'form': form})

@login_required
def complaint_list(request):
    """List all complaints for the current user"""
    if request.user.role == 'officer':
        complaints = Complaint.objects.all()
    else:
        complaints = Complaint.objects.filter(user=request.user)
    
    return render(request, 'complaints/list.html', {'complaints': complaints})

@login_required
def complaint_detail(request, pk):
    """View a single complaint"""
    complaint = get_object_or_404(Complaint, id=pk)
    
    # Check permissions
    if request.user.role != 'officer' and complaint.user != request.user:
        messages.error(request, "You don't have permission to view this complaint.")
        return redirect('complaint_list')
    
    return render(request, 'complaints/detail.html', {'complaint': complaint})

@login_required
@officer_required
def update_complaint(request, pk):
    """Update complaint status (for officers)"""
    complaint = get_object_or_404(Complaint, id=pk)
    
    # Only officers can update
    if request.user.role != 'officer':
        messages.error(request, "Only officers can update complaints.")
        return redirect('complaint_list')
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status:
            complaint.status = status
            complaint.save()
            messages.success(request, f'Complaint status updated to {status}')
            return redirect('complaint_list')
    
    return render(request, 'complaints/update.html', {'complaint': complaint})

@login_required
@officer_required
def officer_complaint_list(request):
    """Officer view for all complaints"""
    complaints = Complaint.objects.all().order_by('-created_at')
    
    # Statistics
    total = complaints.count()
    pending = complaints.filter(status='pending').count()
    investigating = complaints.filter(status='investigating').count()
    resolved = complaints.filter(status='resolved').count()
    closed = complaints.filter(status='closed').count()
    
    # By type
    by_type = complaints.values('category').annotate(count=Count('id'))
    
    # By service provider
    by_provider = complaints.values('company').annotate(count=Count('id'))
    
    context = {
        'complaints': complaints,
        'total': total,
        'pending': pending,
        'investigating': investigating,
        'resolved': resolved,
        'closed': closed,
        'by_type': by_type,
        'by_provider': by_provider,
    }
    
    return render(request, 'complaints/officer_list.html', context)


@login_required
@officer_required
def officer_complaint_detail(request, pk):
    """Officer view for a single complaint"""
    complaint = get_object_or_404(Complaint, id=pk)
    updates = complaint.updates.all().order_by('-created_at')
    
    context = {
        'complaint': complaint,
        'updates': updates,
    }
    
    return render(request, 'complaints/officer_detail.html', context)


@login_required
@officer_required
def officer_complaint_action(request, pk):
    """Process complaint actions (update status, assign, resolve)"""
    complaint = get_object_or_404(Complaint, id=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'assign':
            # Auto-assign to current officer
            old_status = complaint.status
            complaint.assigned_to = request.user
            complaint.status = 'investigating'
            complaint.save()
            
            # Create update record
            ComplaintUpdate.objects.create(
                complaint=complaint,
                comment=f"Assigned to {request.user.username}. {notes}",
                updated_by=request.user,
                status_before=old_status,
                status_after='investigating'
            )
            
            messages.success(request, f'Complaint #{complaint.id} assigned to you.')
            
        elif action == 'update_status':
            new_status = request.POST.get('status')
            if new_status:
                old_status = complaint.status
                complaint.status = new_status
                complaint.save()
                
                # Create update record
                ComplaintUpdate.objects.create(
                    complaint=complaint,
                    comment=notes or f"Status changed from {old_status} to {new_status}",
                    updated_by=request.user,
                    status_before=old_status,
                    status_after=new_status
                )
                
                messages.success(request, f'Complaint #{complaint.id} status updated to {new_status}.')
        
        elif action == 'resolve':
            old_status = complaint.status
            complaint.status = 'resolved'
            complaint.resolved_at = timezone.now()
            complaint.resolution_summary = notes
            complaint.save()
            
            # Create update record
            ComplaintUpdate.objects.create(
                complaint=complaint,
                comment=f"Complaint resolved. {notes}",
                updated_by=request.user,
                status_before=old_status,
                status_after='resolved'
            )
            
            messages.success(request, f'Complaint #{complaint.id} has been resolved.')
        
        elif action == 'close':
            old_status = complaint.status
            complaint.status = 'closed'
            complaint.save()
            
            ComplaintUpdate.objects.create(
                complaint=complaint,
                comment=f"Complaint closed. {notes}",
                updated_by=request.user,
                status_before=old_status,
                status_after='closed'
            )
            
            messages.info(request, f'Complaint #{complaint.id} has been closed.')
        
        return redirect('officer_complaint_detail', pk=complaint.id)
    
    return redirect('officer_complaint_list')