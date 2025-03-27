from .models import *
from rest_framework import  serializers

class create_attendance_serializer(serializers.Serializer):
    employee_id = serializers.PrimaryKeyRelatedField(queryset=employee.objects.all(), required=True)
    date = serializers.DateField(required = True)
    checkin_entry = serializers.DateTimeField(required = False)
    checkout_entry = serializers.DateTimeField(required = False)