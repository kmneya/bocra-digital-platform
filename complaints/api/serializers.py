from rest_framework import serializers
from ..models import Complaint
from ..utils import get_sla_status


class ComplaintSerializer(serializers.ModelSerializer):

    sla_status = serializers.SerializerMethodField()

    def get_sla_status(self, obj):
        return get_sla_status(obj)

    class Meta:
        model = Complaint
        fields = ['status', 'assigned_to', 'priority']
        read_only_fields = ['user', 'status', 'created_at']