from rest_framework.decorators import api_view
from rest_framework.response import Response
from complaints.models import Complaint

@api_view(['GET'])
def stats(request):
    data = {
        "total_complaints": Complaint.objects.count(),
        "resolved": Complaint.objects.filter(status='resolved').count(),
        "pending": Complaint.objects.filter(status='pending').count(),
    }
    return Response(data)