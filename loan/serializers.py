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
    reasons = serializers.CharField(required=False)
    repayment_type = serializers.CharField(required=True)
    percentage_amount = serializers.FloatField(required=False)
    fixed_amount = serializers.FloatField(required=False)
    # status = serializers.CharField(max_length=50)
    # created_at = serializers.DateTimeField(datetime.now())
    # updated_at = serializers.DateTimeField()
    # is_deleted = serializers.BooleanField()

    def validate(self, data):
        loan_type = data.get('loan_type').lower()
        loan_amount = data.get('loan_amount')
        percentage_amount = data.get('percentage_amount')
        fixed_amount = data.get('fixed_amount')

        if loan_type not in ('loan','advance'):
            raise serializers.ValidationError("Loan type can only be loan or advance")
        
        if loan_type == 'loan':
            if percentage_amount is None and fixed_amount is None:
                raise serializers.ValidationError("Percentage amount or fixed amount must be provided")
            if percentage_amount is not None and fixed_amount is not None:
                raise serializers.ValidationError("Both, Percentage amount and fixed amount should not be provided")
            if percentage_amount is not None:
                if percentage_amount <= 0 or percentage_amount > 100:
                    raise serializers.ValidationError("Percentage amount should be between 1 and 100")
            if fixed_amount is not None:
                if fixed_amount <= 0:
                    raise serializers.ValidationError("Fixed amount must be greater than zero")
        if loan_type =='advance':
            if loan_amount is None:
                raise serializers.ValidationError("Loan amount should not be provided for advance")
            if loan_amount<=0:
                raise serializers.ValidationError("Loan amount cannot be negative and zero")
        return data


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

    
    def validate(self, data):
        loan_type = data.get('loan_type').lower()
        loan_amount = data.get('loan_amount')
        percentage_amount = data.get('percentage_amount')
        fixed_amount = data.get('fixed_amount')

        if loan_type not in ('loan','advance'):
            raise serializers.ValidationError("Loan type can only be loan or advance")
        
        if loan_type == 'loan':
            if loan_amount<=0:
                raise serializers.ValidationError("Loan amount cannot be negative and zero")
            if percentage_amount is None and fixed_amount is None:
                raise serializers.ValidationError("Percentage amount or fixed amount must be provided")
            if percentage_amount is not None and fixed_amount is not None:
                raise serializers.ValidationError("Both, Percentage amount and fixed amount should not be provided")
            if percentage_amount is not None:
                if percentage_amount <= 0 or percentage_amount > 100:
                    raise serializers.ValidationError("Percentage amount should be between 1 and 100")
            if fixed_amount is not None:
                if fixed_amount <= 0:
                    raise serializers.ValidationError("Fixed amount must be greater than zero")
        if loan_type =='advance':
            if loan_amount is None:
                raise serializers.ValidationError("Loan amount should not be provided for advance")
            if loan_amount<=0:
                raise serializers.ValidationError("Loan amount cannot be negative and zero")
        return data
    

        # if data['loan_amount'] <= 0:
        #     raise serializers.ValidationError("Loan amount cannot be negative and zero")
        # if data['percentage_amount'] is not None:
        #     if data['percentage_amount'] <= 0 or data['percentage_amount'] > 100:
        #         raise serializers.ValidationError("Percentage amount should be between 1 and 100")
        # if data['fixed_amount'] is not None:
        #     if data['fixed_amount'] <= 0:
        #         raise serializers.ValidationError("Fixed amount must be greater than zero")
        # if data['loan_type'].lower() not in ('loan','advance'):
        #     raise serializers.ValidationError("Loan type can only be loan or advance")
        # return data


class LoanStatusUpdateSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=50)

    def validate(self, data):
        status = data.get('status').lower()
        if status not in ('pending','accepted','rejected'):
            raise serializers.ValidationError("Status can only be pending, approved or rejected")
        # print(data, "data form serializer")
        return data