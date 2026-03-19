from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ComplaintForm

@login_required
def create_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            return redirect('citizen_dashboard')
    else:
        form = ComplaintForm()

    return render(request, 'complaints/create.html', {'form': form})