from django.urls import path
from .views import *

urlpatterns = [
    path('citizen/', citizen_dashboard, name='citizen_dashboard'),
    path('officer/', officer_dashboard, name='officer_dashboard'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
]