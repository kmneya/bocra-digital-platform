from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_complaint, name='create_complaint'),
    path('', views.complaint_list, name='complaint_list'),
    path('<int:pk>/', views.complaint_detail, name='complaint_detail'),
    path('<int:pk>/update/', views.update_complaint, name='update_complaint'),
    path('officer/', views.officer_complaint_list, name='officer_complaint_list'),
    path('officer/<int:pk>/', views.officer_complaint_detail, name='officer_complaint_detail'),
    path('officer/<int:pk>/action/', views.officer_complaint_action, name='officer_complaint_action'),
    ]