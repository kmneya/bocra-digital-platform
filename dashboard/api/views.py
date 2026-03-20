from rest_framework.decorators import api_view
from rest_framework.response import Response
from complaints.models import Complaint
from django.db.models import Count


@api_view(['GET'])
def stats(request):
    data = {
        "total_complaints": Complaint.objects.count(),
        "resolved": Complaint.objects.filter(status='resolved').count(),
        "pending": Complaint.objects.filter(status='pending').count(),
    }
    return Response(data)


@api_view(['GET'])
def advanced_stats(request):
    data = {
        "total_complaints": Complaint.objects.count(),
        "resolved": Complaint.objects.filter(status='resolved').count(),
        "pending": Complaint.objects.filter(status='pending').count(),

        # 🔥 complaints per category
        "by_category": list(
            Complaint.objects.values('category__name')
            .annotate(count=Count('id'))
        ),

        # 🔥 status distribution
        "by_status": list(
            Complaint.objects.values('status')
            .annotate(count=Count('id'))
        ),
    }

    return Response(data)

@api_view(['GET'])
def qos_data(request):
    data = [
        {"provider": "Mascom", "speed": "40 Mbps", "latency": "25 ms"},
        {"provider": "Orange", "speed": "35 Mbps", "latency": "30 ms"},
        {"provider": "BTC", "speed": "20 Mbps", "latency": "50 ms"},
    ]
    return Response(data)