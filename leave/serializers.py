from rest_framework import  serializers
from employee.models import employee
from .models import employee_leave_balances
from attendance.models import employee_applied_leaves

class create_leavebalance_serializer(serializers.Serializer):
	employee_id = serializers.PrimaryKeyRelatedField(queryset=employee.objects.all(), required=True)
	sick_leave = serializers.FloatField(required = True)
	casual_leave = serializers.FloatField(required = True)
	permissions = serializers.FloatField(required = True)
	compensation_leave = serializers.FloatField(required = True)

class get_leavebalance_serializer(serializers.ModelSerializer):
	
	class Meta:
		model = employee_leave_balances
		fields = "__all__"
		
class create_employee_applied_leaves(serializers.Serializer):
	employee_id = serializers.PrimaryKeyRelatedField(queryset=employee.objects.all(), required=True)
	start_date = serializers.DateField(required = True)
	end_date = serializers.DateField(required = True)
	leave_type = serializers.CharField(required = True)
	reason = serializers.CharField(required = True)
	status = serializers.CharField(required = True)

	def validate(self, data):
		if data['start_date'] > data['end_date']: 
			raise serializers.ValidationError( "End date should be greater than start date")

		return data

class create_employee_applied_leaves_days(serializers.Serializer):
	applied_leave_request_id = serializers.PrimaryKeyRelatedField(queryset=employee_applied_leaves.objects.all(), required=True)
	leave_date = serializers.DateField(required = True)
	session = serializers.CharField(required = True)
	comment = serializers.CharField(required = True)
	status = serializers.CharField(required = True)