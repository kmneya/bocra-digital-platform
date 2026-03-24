"""
URL configuration for bocra_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .views import home, about, contact
from users.views import redirect_dashboard

schema_view = get_schema_view(
    openapi.Info(
        title="BOCRA API",
        default_version='v1',
        description="API documentation for BOCRA Digital Platform",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('auth/', include('users.urls')),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('api/', include('bocra_portal.api_urls')), 
    path('dashboard/', include('dashboard.urls')),
    path('complaints/', include('complaints.urls')),
    path('licenses/', include('licensing.urls')),
    path('redirect-dashboard/', redirect_dashboard, name='redirect_dashboard'),
    #Api
    path('api/', include('complaints.api.urls')),
    path('api/dashboard/', include('dashboard.api.urls')),

    # Swagger endpoints
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
]
