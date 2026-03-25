from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import CitizenRegistrationForm
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm

class UserLoginView(LoginView):
    template_name = 'users/login.html'
    
    def get(self, request, *args, **kwargs):
        # Clear only non-login related messages
        # Keep error messages that belong here
        storage = messages.get_messages(request)
        for message in storage:
            # Don't clear messages that should stay
            pass
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Handle successful login"""
        response = super().form_valid(form)
        messages.success(self.request, f'Welcome back, {self.request.user.username}!')
        return response
    
    def form_invalid(self, form):
        """Handle failed login - show error at the bottom of the card"""
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)


def logout_view(request):
    """Handle logout"""
    if request.method == 'POST':
        username = request.user.username if request.user.is_authenticated else None
        logout(request)
        
        # Clear all messages after logout
        storage = messages.get_messages(request)
        storage.used = True
        
        if username:
            messages.success(request, f'You have been successfully logged out, {username}.')
        return redirect('login')
    return redirect('login')


def register(request):
    """Handle user registration"""
    if request.method == 'POST':
        form = CitizenRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'citizen'
            user.save()

            login(request, user)
            messages.success(request, f'Welcome to BOCRA Digital Platform, {user.username}!')
            return redirect('redirect_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CitizenRegistrationForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def redirect_dashboard(request):
    """Redirect to appropriate dashboard based on role"""
    if request.user.role == 'officer':
        return redirect('officer_dashboard')
    elif request.user.role == 'admin':
        return redirect('admin_dashboard')
    else:
        return redirect('citizen_dashboard')
    

@login_required
def update_profile(request):
    """Allow users to update their contact information"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('citizen_dashboard')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'users/profile.html', {'form': form})