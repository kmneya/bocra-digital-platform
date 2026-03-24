from django.contrib import messages
from django.shortcuts import render

def home(request):
    messages.get_messages(request).used = True
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def documents(request):
    return render(request, 'documents/list.html')