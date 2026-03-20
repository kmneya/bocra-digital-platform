from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import now
from notification.models import Notification
from ..models import LicenseApplication
from .serializers import LicenseSerializer

class LicenseViewSet(viewsets.ModelViewSet):
    queryset = LicenseApplication.objects.all()
    serializer_class = LicenseSerializer

    def perform_create(self, serializer):
        application = serializer.save(user=self.request.user)

        Notification.objects.create(
            user=self.request.user,
            message=f"License application '{application.business_name}' submitted."
        )

    def get_queryset(self):
        user = self.request.user

        if user.role == 'citizen':
            return LicenseApplication.objects.filter(user=user)

        return LicenseApplication.objects.all()
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        application = self.get_object()

        if request.user.role not in ['officer', 'admin']:
            return Response({"error": "Not authorized"}, status=403)

        application.status = 'approved'
        application.reviewed_by = request.user
        application.reviewed_at = now()
        application.save()

        Notification.objects.create(
            user=application.user,
            message="Your license application was approved"
        )

        return Response({"message": "Application approved"})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        application = self.get_object()

        application.status = 'rejected'
        application.reviewed_by = request.user
        application.reviewed_at = now()
        application.save()

        Notification.objects.create(
            user=application.user,
            message="Your license application was rejected"
        )

        return Response({"message": "Application rejected"})