from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # 🔥 Role-based redirect
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'officer':
                return redirect('officer_dashboard')
            else:
                return redirect('citizen_dashboard')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')