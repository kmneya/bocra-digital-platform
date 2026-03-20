from rest_framework import serializers
from ..models import LicenseApplication

class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseApplication
        fields = '__all__'
        read_only_fields = ['user', 'status']