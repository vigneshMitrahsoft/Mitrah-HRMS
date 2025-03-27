from .models import *
from rest_framework import  serializers
from django.contrib.auth.hashers import make_password

class company_serializer(serializers.ModelSerializer):
    class Meta:
        model = company 
        fields = "__all__"


class get_serializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    company_id = serializers.PrimaryKeyRelatedField(queryset=company.objects.all(), required=True)
    first_name = serializers.CharField(required = True)
    last_name = serializers.CharField(required = True)
    email = serializers.EmailField(required = True)
    date_of_birth = serializers.DateField(required = True)
    address = serializers.CharField(required = True)
    role_id = serializers.PrimaryKeyRelatedField(queryset=employee_role.objects.all(), required=True)
    date_of_joining = serializers.DateField(required = True)
    type_id = serializers.PrimaryKeyRelatedField(queryset=employee_type.objects.all(), required=True)

class create_serializer(serializers.Serializer):
    company_id = serializers.IntegerField(required=True)
    first_name = serializers.CharField(required = True)
    last_name = serializers.CharField(required = True)
    email = serializers.EmailField(required = True)
    password = serializers.CharField(required = True)
    date_of_birth = serializers.DateField(required = True)
    address = serializers.CharField(required = True)
    role_id = serializers.PrimaryKeyRelatedField(queryset=employee_role.objects.all(), required=True)
    date_of_joining = serializers.DateField(required = True)
    type_id = serializers.PrimaryKeyRelatedField(queryset=employee_type.objects.all(), required=True)

    # def get_company_id(self, data):
    #     return company.objects.get(company_id = data.company_id)

    # def get_password(self, data):
    #     return make_password(data['password'])

class update_serializer(serializers.Serializer):
    company_id = serializers.PrimaryKeyRelatedField(queryset=company.objects.all(), required=False)
    first_name = serializers.CharField(required = False)
    last_name = serializers.CharField(required = False)
    email = serializers.EmailField(required = False)
    password = serializers.CharField(required = False)
    date_of_birth = serializers.DateField(required = False)
    address = serializers.CharField(required = False)
    role_id = serializers.PrimaryKeyRelatedField(queryset=employee_role.objects.all(), required=False)
    date_of_joining = serializers.DateField(required = False)
    type_id = serializers.PrimaryKeyRelatedField(queryset=employee_type.objects.all(), required=False)
