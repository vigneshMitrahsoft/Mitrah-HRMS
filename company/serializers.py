from rest_framework import serializers
from .models import company
import os

class companySerializer(serializers.ModelSerializer):

	class Meta:
		model = company
		fields = '__all__'
		
	def to_representation(self, instance):
		request = self.context['request']  
		data = super().to_representation(instance)
		request_url = request.build_absolute_uri('/')[:-1] 
		file_directory = '/assets/company_logo/'
		if data.get('company_logo_path'):
			filename = os.path.basename(data['company_logo_path'])
			data['company_logo_path'] = f"{request_url}{file_directory}{filename}"
		else:
			data['company_logo_path'] = ""
		data = {key: "" if value is None else value for key, value in data.items()}
		return data

class companyCreateSerializer(serializers.Serializer):
	company_name = serializers.CharField()
	address =serializers.CharField()
	company_logo = serializers.ImageField(required = False)
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
	permission_hours = serializers.FloatField()
	pay_cycle_day = serializers.IntegerField(min_value = 1, max_value = 31)

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
	permission_hours = serializers.FloatField()