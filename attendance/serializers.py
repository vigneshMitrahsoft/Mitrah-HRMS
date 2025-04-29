
from .models import attendance_entries, employee,employee_attendance,employees_attendance_info
from rest_framework import  serializers

class create_attendance_serializer(serializers.Serializer):
	employee_id = serializers.PrimaryKeyRelatedField(queryset=employee.objects.all(), required=True)
	date = serializers.DateField(required = True)
	check_in = serializers.DateTimeField(required = False)
	check_out = serializers.DateTimeField(required = False)

class attendance_entry_serializer(serializers.Serializer):
	attendance_id = serializers.PrimaryKeyRelatedField(queryset=employee_attendance.objects.all(), required=True)
	checkin_entry = serializers.DateTimeField(required = False)
	checkout_entry = serializers.DateTimeField(required = False)

class attendance_info_serializer(serializers.ModelSerializer):
	class Meta:
		model = employees_attendance_info
		fields = "__all__"

class attendance_serializer(serializers.ModelSerializer):
	class Meta:
		model = employee_attendance
		fields = "__all__"

class create_attendance_byinfo_serializer(serializers.Serializer):
	employee_id = serializers.PrimaryKeyRelatedField(queryset=employee.objects.all(), required=True)
	date = serializers.DateField(required = True)

class atttendance_info_post_serializer(serializers.Serializer):
	employee_id = serializers.PrimaryKeyRelatedField(queryset=employee.objects.all(), required=True)
	attendance_id = serializers.PrimaryKeyRelatedField(queryset=employee_attendance.objects.all(), required=True)
	date = serializers.DateField(required = True)
	status = serializers.CharField(required = True)

class get_employee_attendance_serializer(serializers.Serializer):
	date = serializers.DateField(required = True)
	day = serializers.CharField(required = True)
	is_week_off = serializers.BooleanField(required = False)
	attendance_status = serializers.CharField(required = False)
	leave_status = serializers.CharField(required = False)
	check_in = serializers.DateTimeField(required = False)
	check_out = serializers.DateTimeField(required = False)
	effective_hours = serializers.TimeField(required = False)
	total_hours = serializers.TimeField(required = False)

class attendance_entry_model(serializers.ModelSerializer):
	class Meta:
		model = attendance_entries
		fields = ['checkin_entry','checkout_entry']

class entries_serializer(serializers.Serializer):
	entries = serializers.CharField(required = True)

class get_attendance_info_serializer(serializers.Serializer):
	first_name = serializers.CharField(required = True)
	last_name = serializers.CharField(required = True)
	status = serializers.CharField(required = True)
	check_in = serializers.DateTimeField(required = False)
	check_out = serializers.DateTimeField(required = False, allow_null=True)
	entries = attendance_entry_model(many = True)

