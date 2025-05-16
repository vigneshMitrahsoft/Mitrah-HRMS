from rest_framework import serializers
from employee.models import employee_type

class RegisterSerializer(serializers.Serializer):
    company_name = serializers.CharField(required = True)
    address = serializers.CharField(required = True)
    first_name = serializers.CharField(required = True)
    last_name = serializers.CharField(required = True)
    email = serializers.EmailField(required = True)
    password = serializers.CharField(required = True)
    type_id = serializers.PrimaryKeyRelatedField(queryset=employee_type.objects.all(), required=True)
