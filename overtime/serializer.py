from rest_framework import serializers
from .models import Overtime
from employee.models import employee

class overtimeSerializer(serializers.ModelSerializer):
	class Meta:
		model = Overtime
		fields = '__all__'	

class createOvertimeSerializer(serializers.Serializer):
	# employee_id = serializers.PrimaryKeyRelatedField(queryset = employee.objects.all()) 
	project_name = serializers.CharField(max_length=100)
	requested_hours = serializers.FloatField(required=True)
	start_date = serializers.DateTimeField(required=True)
	end_date = serializers.DateTimeField(required=True)
	# credicted_hours = serializers.FloatField(required=True)
