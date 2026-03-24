from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Complaint
from .forms import ComplaintForm
from users.decorators import citizen_required, officer_required

@login_required
@citizen_required
def create_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            messages.success(request, 'Your complaint has been submitted successfully!')
            return redirect('redirect_dashboard')
    else:
        form = ComplaintForm()

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