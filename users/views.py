from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from .forms import CitizenRegistrationForm
from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        form = CitizenRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'citizen'  # 🔥 force role
            user.save()

            login(request, user)  # auto login after register

            return redirect('citizen_dashboard')

    else:
        form = CitizenRegistrationForm()

    return render(request, 'users/register.html', {'form': form})



class UserLoginView(LoginView):
    template_name = 'users/login.html'
