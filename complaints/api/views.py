from rest_framework import viewsets, permissions
from ..models import Complaint
from .serializers import ComplaintSerializer
from .permissions import IsOfficerOrAdmin

class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user

        # 🔥 Role-based data filtering
        if user.role == 'citizen':
            return Complaint.objects.filter(user=user)

        elif user.role == 'officer':
            return Complaint.objects.all()

        return Complaint.objects.all()
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOfficerOrAdmin()]
        return [permissions.IsAuthenticated()]