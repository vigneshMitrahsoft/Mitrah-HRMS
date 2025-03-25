from rest_framework import serializers
from .models import LoanDeduction, Repayment


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
    # requested_date = serializers.DateTimeField()
    # approved_date = serializers.DateTimeField   
    reasons = serializers.CharField()
    repayment_period = serializers.IntegerField(required=True)
    monthly_emi = serializers.FloatField(required=True)
    # status = serializers.CharField(max_length=50)
    # created_at = serializers.DateTimeField()
    # updated_at = serializers.DateTimeField()
    # is_deleted = serializers.BooleanField()


class UpdateloanSerializer(serializers.Serializer):
    loan_type = serializers.CharField(max_length=100)
    loan_amount = serializers.FloatField(required=True)  
    # employee_id = serializers.IntegerField()
    # requested_date = serializers.DateTimeField()
    # approved_date = serializers.DateTimeField   
    reasons = serializers.CharField(required=True)
    repayment_period = serializers.IntegerField(required=True)
    monthly_emi = serializers.FloatField(required=True)
    # status = serializers.CharField(max_length=50)
    # created_at = serializers.DateTimeField()
    # updated_at = serializers.DateTimeField()
    # is_deleted = serializers.BooleanField()