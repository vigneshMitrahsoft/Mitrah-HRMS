from .models import *
from rest_framework import  serializers

class create_attendance_serializer(serializers.Serializer):
    employee_id = serializers.PrimaryKeyRelatedField(queryset=employee.objects.all(), required=True)
    date = serializers.DateField(required = True)
    check_in = serializers.DateTimeField(required = False)
    check_out = serializers.DateTimeField(required = False)

class attendance_entry_serializer(serializers.Serializer):
    attendance_id = serializers.PrimaryKeyRelatedField(queryset=employee_attendance.objects.all(), required=True)
    checkin_entry = serializers.DateTimeField(required = False)
    checkout_entry = serializers.DateTimeField(required = False)

class attendance_info_serializer(serializers.ModelSerializer):
    class Meta:
        model = employees_attendance_info
        fields = "__all__"