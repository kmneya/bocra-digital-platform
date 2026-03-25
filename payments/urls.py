from django.urls import path
from . import views

urlpatterns = [
    path('initiate/<int:license_id>/', views.initiate_payment, name='initiate_payment'),
    path('checkout/<int:payment_id>/', views.payment_checkout, name='payment_checkout'),
    path('success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('status/<int:payment_id>/', views.payment_status, name='payment_status'),
    path('payments/', views.payment_list, name='payment_list'),
    path('verify/<int:payment_id>/', views.verify_payment, name='verify_payment'),
]