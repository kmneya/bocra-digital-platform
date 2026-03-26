from django.db.models import Count, Q
from complaints.models import Complaint
from licensing.models import LicenseApplication
from users.models import User

def admin_stats(request):
    """Add statistics to admin context"""
    if request.user.is_staff:
        return {
            'total_complaints': Complaint.objects.count(),
            'pending_complaints': Complaint.objects.filter(status='pending').count(),
            'resolved_complaints': Complaint.objects.filter(status='resolved').count(),
            'total_licenses': LicenseApplication.objects.count(),
            'pending_licenses': LicenseApplication.objects.filter(status='pending').count(),
            'approved_licenses': LicenseApplication.objects.filter(status='approved').count(),
            'total_users': User.objects.count(),
            'officer_count': User.objects.filter(role='officer').count(),
            'citizen_count': User.objects.filter(role='citizen').count(),
        }
    return {}