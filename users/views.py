from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from .forms import CitizenRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def redirect_dashboard(request):
    if request.user.role == 'officer':
        return redirect('officer_dashboard')
    else:
        return redirect('citizen_dashboard')

def register(request):
    if request.method == 'POST':
        form = CitizenRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'citizen'  # 🔥 force role
            user.save()

            login(request, user)  # auto login after register

            return redirect('redirect_dashboard')

    else:
        form = CitizenRegistrationForm()

    return render(request, 'users/register.html', {'form': form})

def logout_view(request):
    """Handle logout with POST and GET"""
    if request.method == 'POST':
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect('login')
    else:
        # For GET requests, show confirmation page or redirect
        return redirect('login')



class UserLoginView(LoginView):
    template_name = 'users/login.html'
    
    def get(self, request, *args, **kwargs):
        messages.get_messages(request).used = True
        return super().get(request, *args, **kwargs)
