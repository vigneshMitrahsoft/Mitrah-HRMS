from rest_framework import serializers
from .models import LoanDeduction, Repayment
from datetime import datetime


class loanSerializer(serializers.ModelSerializer):
	class Meta:
		model = LoanDeduction
		fields = '__all__'


class repaymentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Repayment   
		fields = '__all__'


class createLoanSerializer(serializers.Serializer):
	loan_type = serializers.CharField(max_length=100)
	loan_amount = serializers.FloatField(required=True)  
	# employee_id = serializers.IntegerField()
	# requested_date = serializers.DateTimeField(datetime.now())
	# approved_date = serializers.DateTimeField   
	reasons = serializers.CharField(required=False)
	repayment_type = serializers.CharField(required=True)
	percentage_amount = serializers.FloatField(required=False)
	fixed_amount = serializers.FloatField(required=False)
	tenure = serializers.FloatField(required= False)
	# status = serializers.CharField(max_length=50)
	# created_at = serializers.DateTimeField(datetime.now())
	# updated_at = serializers.DateTimeField()
	# is_deleted = serializers.BooleanField()

	def validate(self, data):
		data['loan_type'] = data.get('loan_type', "").strip().lower()
		data['repayment_type'] = data.get('repayment_type', "").strip().lower()
		loan_type = data.get('loan_type')
		repayment_type = data.get('repayment_type')
		loan_amount = data.get('loan_amount')
		percentage_amount = data.get('percentage_amount')
		fixed_amount = data.get('fixed_amount')
		tenure = data.get('tenure')

		if loan_type not in ('loan','advance'):
			raise serializers.ValidationError("Loan type can only be loan or advance")
		
		if loan_type == 'loan':
			if loan_amount<=0:
				raise serializers.ValidationError("Loan amount cannot be negative and zero")
			if percentage_amount is None and fixed_amount is None and tenure is None:
				raise serializers.ValidationError("Percentage amount or fixed amount or tenure must be provided")
			if percentage_amount is not None and fixed_amount is not None and tenure is not None:
				raise serializers.ValidationError("Both, Percentage amount and fixed amount, tenure should not be provided")
			if percentage_amount is not None:
				if percentage_amount <= 0 or percentage_amount > 100:
					raise serializers.ValidationError("Percentage amount should be between 1 and 100")
			if fixed_amount is not None:
				if fixed_amount <= 0:
					raise serializers.ValidationError("Fixed amount must be greater than zero")
			if tenure is not None:
				if tenure <=0:
					raise serializers.ValidationError("Tenure must be greater than zero")
		if loan_type == 'advance':
			if loan_amount is None:
				raise serializers.ValidationError("Loan amount should not be provided for advance")
			if loan_amount<=0:
				raise serializers.ValidationError("Loan amount cannot be negative and zero")
		if repayment_type not in ('percentage','fixed','tenure'):
			raise serializers.ValidationError("Repayment type can only be percentage or fixed")
		return data


class updateLoanSerializer(serializers.Serializer):
	loan_type = serializers.CharField(max_length=100)
	loan_amount = serializers.FloatField(required=False)  
	# employee_id = serializers.IntegerField()
	# requested_date = serializers.DateTimeField()
	# approved_date = serializers.DateTimeField   
	reasons = serializers.CharField(required=False)
	repayment_type = serializers.CharField(required=False)
	percentage_amount = serializers.FloatField(required=False)
	fixed_amount = serializers.FloatField(required=False)
	tenure = serializers.FloatField(required = False)
	# status = serializers.CharField(max_length=50)
	# created_at = serializers.DateTimeField()
	# updated_at = serializers.DateTimeField(datetime.now())  
	# is_deleted = serializers.BooleanField()

	
	def validate(self, data):
		data['loan_type'] = data.get('loan_type', "").strip().lower()
		data['repayment_type'] = data.get('repayment_type', "").strip().lower()
		loan_type = data.get('loan_type')
		repayment_type = data.get('repayment_type')
		loan_amount = data.get('loan_amount')
		percentage_amount = data.get('percentage_amount')
		fixed_amount = data.get('fixed_amount')
		tenure = data.get('tenure')

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
			if tenure is not None:
				if tenure <=0:
					raise serializers.ValidationError("Tenure must be greater than zero")
		if loan_type =='advance':
			if loan_amount is None:
				raise serializers.ValidationError("Loan amount should not be provided for advance")
			if loan_amount<=0:
				raise serializers.ValidationError("Loan amount cannot be negative and zero")
		if repayment_type not in ('percentage','fixed','tenure'):
			raise serializers.ValidationError("Repayment type can only be percentage or fixed")
		return data


class loanStatusUpdateSerializer(serializers.Serializer):
	status = serializers.CharField(max_length=50)

	def validate(self, data):
		status = data.get('status').strip().lower()
		if status not in ('pending','accepted','rejected'):
			raise serializers.ValidationError("Status can only be pending, accepted or rejected")
		return data
	

class repaymentCreateSerializer(serializers.Serializer):
	# loan_id = serializers.PrimaryKeyRelatedField(queryset = LoanDeduction.objects.all())
	payment_date = serializers.DateTimeField()
	amount_paid = serializers.FloatField()
	remaining_balance = serializers.FloatField()



