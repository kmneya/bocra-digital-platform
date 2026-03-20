from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Notification

@api_view(['GET'])
def user_notifications(request):
    notifications = Notification.objects.filter(user=request.user)

    data = [
        {
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at
        }
        for n in notifications
    ]

    return Response(data)