from rest_framework import viewsets, permissions
from ..models import Complaint
from .serializers import ComplaintSerializer
from .permissions import IsOfficerOrAdmin
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import now
from users.models import User
from ..models import ComplaintUpdate
from notification.models import Notification

class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        officers = User.objects.filter(role='officer')

        assigned_officer = officers.order_by('?').first()  # random assignment

        complaint = serializer.save(
            user=self.request.user,
            assigned_to=assigned_officer
        )
        
        Notification.objects.create(
        user=self.request.user,
        message=f"Your complaint '{complaint.title}' has been submitted."
        )
        Notification.objects.create(
        user=assigned_officer,
        message=f"You have been assigned a new complaint: {complaint.title}"
        )

    def get_queryset(self):
        user = self.request.user

        # 🔥 Role-based data filtering
        if user.role == 'citizen':
            return Complaint.objects.filter(user=user)

        elif user.role == 'officer':
            return Complaint.objects.all()

        return Complaint.objects.all()
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        complaint = self.get_object()

        # 🔒 Only officers/admins allowed
        if request.user.role not in ['officer', 'admin']:
            return Response({"error": "Not authorized"}, status=403)

        status_value = request.data.get('status')

        complaint.status = status_value

        if status_value == 'resolved':
            complaint.resolved_at = now()

        complaint.save()

        ComplaintUpdate.objects.create(
            complaint=complaint,
            comment=f"Status changed to {status_value}",
            updated_by=request.user
        )
        Notification.objects.create(
            user=complaint.user,
            message=f"Your complaint status changed to {status_value}"
        )

        return Response({"message": "Status updated"})
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOfficerOrAdmin()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        complaint = self.get_object()

        if request.user.role != 'admin':
            return Response({"error": "Only admin can assign"}, status=403)

        officer_id = request.data.get('officer_id')

        complaint.assigned_to_id = officer_id
        complaint.save()

        return Response({"message": "Assigned successfully"})