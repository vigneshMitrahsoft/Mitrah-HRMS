import datetime
from rest_framework import serializers
from .models import Overtime
from employee.models import employee
from rest_framework.exceptions import APIException


def calculated_requested_hours(obj):
		today = datetime.date.today()
		start_time = datetime.datetime.combine(today, obj.start_time)
		end_time = datetime.datetime.combine(today, obj.end_time)

		if start_time >= end_time:
			raise APIException(detail={"statuscode": 400, "status": "error", "message": "Start time must be before end time"})
		
		if start_time == end_time:
			raise APIException(detail={"statuscode": 400, "status": "error", "message": "Start time and end time cannot be the same"})

		duration = end_time - start_time

		if duration.total_seconds() < 0:
			duration += datetime.timedelta(days=1)

		return round(duration.total_seconds() / 3600,2)  # Convert seconds to hours

class overtimeSerializer(serializers.ModelSerializer):
	requested_hours = serializers.SerializerMethodField()
	class Meta:
		model = Overtime
		fields = '__all__'	
	
	def get_requested_hours(self, obj):
		return calculated_requested_hours(obj)

class createOvertimeSerializer(serializers.Serializer):
	# employee_id = serializers.PrimaryKeyRelatedField(queryset = employee.objects.all()) 
	project_name = serializers.CharField(max_length=100)
	# requested_hours = serializers.FloatField(required=True)
	start_time = serializers.TimeField(required=True)
	end_time = serializers.TimeField(required=True)
	# start_date = serializers.DateTimeField(required=True)
	# end_date = serializers.DateTimeField(required=True)
	# credicted_hours = serializers.FloatField(required=True)
	date = serializers.DateField(required=True)
	requested_hours = serializers.SerializerMethodField()

	def validate(self, data):
		start_time = data.get('start_time')
		end_time = data.get('end_time')
		if start_time == end_time:
			raise APIException(detail={"statuscode": 400, "status": "error", "message": "Start time and end time cannot be the same"})
		if start_time >= end_time:
			raise APIException(detail={"statuscode": 400, "status": "error", "message": "Start time must be before end time"})
		return data
	
	def get_requested_hours(self, obj):
		return calculated_requested_hours(obj)
	
class updateOvertimeSerializer(serializers.Serializer):
	# employee_id = serializers.PrimaryKeyRelatedField(queryset = employee.objects.all()) 
	project_name = serializers.CharField(max_length=100)
	# requested_hours = serializers.FloatField(required=True)
	start_time = serializers.TimeField(required=True)
	end_time = serializers.TimeField(required=True)
	# start_date = serializers.DateTimeField(required=True)
	# end_date = serializers.DateTimeField(required=True)
	# credicted_hours = serializers.FloatField(required=True)
	date = serializers.DateField(required=True)
	requested_hours = serializers.SerializerMethodField()

	def validate(self, data):
		start_time = data.get('start_time')
		end_time = data.get('end_time')
		if start_time == end_time:
			raise APIException(detail={"statuscode": 400, "status": "error", "message": "Start time and end time cannot be the same"})
		if start_time >= end_time:
			raise APIException(detail={"statuscode": 400, "status": "error", "message": "Start time must be before end time"})
		return data
	
	def get_requested_hours(self, obj):
		return calculated_requested_hours(obj)
	
class overtimeStatusUpdateSerializer(serializers.Serializer):
	status = serializers.CharField(max_length=50, required=True)

	def validate(self, data):
		status = data.get('status').lower()
		if status not in ('accepted', 'rejected'):
			raise APIException(detail={"statuscode": 400, "status": "error", "message": "Status can only be accepted or rejected"})
		return data