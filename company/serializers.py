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
	basic_pay = serializers.FloatField()
	other_allowances = serializers.FloatField()
	permission_hours = serializers.TimeField()

	def validate(self,data):
		errors = []

		if data['basic_pay'] == 100:
			data['hra'] = 0
			data['other_allowances'] = 0
		if not (0 <= data['basic_pay'] <= 100):
			errors.append("Basic pay percent must be between 0 and 1.")
		if not (0 <= data['hra'] <= 100):
			errors.append("HRA percent must be between 0 and 1.")
		if not (0 <= data['other_allowances'] <= 100):
			errors.append("Other allowance percent must be between 0 and 1.")
		if data['basic_pay'] + data['hra'] + data['other_allowances'] > 100:
			errors.append("Total salary component percentages should not exceed 100%.")
		
		if errors:
			raise serializers.ValidationError(errors)
	
		return data


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
	basic_pay = serializers.FloatField()
	other_allowances = serializers.FloatField()
	permission_hours = serializers.TimeField()

