from django.urls import path
from . import views

urlpatterns = [
    path('', views.license_list, name='license_list'),
    path('apply/', views.apply_license, name='apply_license'),
    path('apply/aircraft/', views.aircraft_license_form, name='aircraft_license_form'),
    path('apply/cellular/', views.cellular_license_form, name='cellular_license_form'),
    path('<int:pk>/', views.license_detail, name='license_detail'),

    path('officer/', views.officer_license_list, name='officer_license_list'),
    path('officer/<int:pk>/', views.officer_license_detail, name='officer_license_detail'),
    path('officer/<int:pk>/action/', views.officer_license_action, name='officer_license_action'),
    path('<int:pk>/review/', views.review_license, name='review_license'),
]

