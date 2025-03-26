from rest_framework import serializers
from .models import LoanDeduction, Repayment
from datetime import datetime


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanDeduction
        fields = '__all__'


class RepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repayment   
        fields = '__all__'


class CreateloanSerializer(serializers.Serializer):
    loan_type = serializers.CharField(max_length=100)
    loan_amount = serializers.FloatField(required=True)  
    # employee_id = serializers.IntegerField()
    # requested_date = serializers.DateTimeField(datetime.now())
    # approved_date = serializers.DateTimeField   
    reasons = serializers.CharField(required=True)
    repayment_type = serializers.CharField(required=True)
    percentage_amount = serializers.FloatField(required=True)
    fixed_amount = serializers.FloatField(required=True)
    # status = serializers.CharField(max_length=50)
    # created_at = serializers.DateTimeField(datetime.now())
    # updated_at = serializers.DateTimeField()
    # is_deleted = serializers.BooleanField()


class UpdateloanSerializer(serializers.Serializer):
    loan_type = serializers.CharField(max_length=100)
    loan_amount = serializers.FloatField(required=False)  
    # employee_id = serializers.IntegerField()
    # requested_date = serializers.DateTimeField()
    # approved_date = serializers.DateTimeField   
    reasons = serializers.CharField(required=False)
    repayment_type = serializers.CharField(required=False)
    percentage_amount = serializers.FloatField(required=False)
    fixed_amount = serializers.FloatField(required=False)
    # status = serializers.CharField(max_length=50)
    # created_at = serializers.DateTimeField()
    # updated_at = serializers.DateTimeField(datetime.now())  
    # is_deleted = serializers.BooleanField()