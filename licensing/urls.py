from django.urls import path
from .views import license_list, license_detail,apply_license,aircraft_license_form

urlpatterns = [
    path('apply/', apply_license, name='apply_license'),
    path('aircraft/', aircraft_license_form, name='aircraft_license_form'),
    path('', license_list, name='license_list'),
    path('<int:pk>/', license_detail, name='license_detail'),
]