from rest_framework import serializers
from .models import company


class companySerializer(serializers.ModelSerializer):

    class Meta:
        model = company
        fields = '__all__'

class companyCreateSerializer(serializers.Serializer):
    company_name = serializers.CharField()
    address =serializers.CharField()
    hra = serializers.FloatField()
    employer_ESI = serializers.FloatField()
    employee_ESI = serializers.FloatField()
    employer_PF = serializers.FloatField()
    employee_PF = serializers.FloatField()
    leave_compensation = serializers.FloatField()
    basic_work_hours = serializers.FloatField()
    sick_leaves = serializers.FloatField()
    casual_leaves = serializers.FloatField()


class companyUpdateSerializer(serializers.Serializer):
    company_name = serializers.CharField()
    address =serializers.CharField()
    hra = serializers.FloatField()
    employer_ESI = serializers.FloatField()
    employee_ESI = serializers.FloatField()
    employer_PF = serializers.FloatField()
    employee_PF = serializers.FloatField()
    leave_compensation = serializers.FloatField()
    basic_work_hours = serializers.FloatField()
    sick_leaves = serializers.FloatField()
    casual_leaves = serializers.FloatField()

