from django.urls import path
from . import views

urlpatterns = [
    path('network-monitoring/', views.network_monitoring_dashboard, name='network_monitoring'),
]