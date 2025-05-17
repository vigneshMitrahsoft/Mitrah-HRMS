from django.db import models

# Create your models here.

class Overtime(models.Model):
	employee_id = models.ForeignKey("employee.Employee", on_delete=models.CASCADE, related_name="overtime", db_column = 'employee_id')
	project_name = models.CharField(max_length=100)
	date = models.DateField(blank=True, null=True)
	start_time = models.TimeField(blank=True, null=True)
	end_time = models.TimeField(blank=True, null=True)
	#requested_hours - it will be the virtual field which will be calculated based on the start time and end time
	credited_hours = models.FloatField(blank=True, null=True)
	status = models.CharField(max_length=50, blank=True, default= 'Pending')
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.CharField(max_length=50, blank=True, null=True)
	updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
	updated_by = models.CharField(max_length=50, blank=True, null=True)
	is_deleted = models.BooleanField(default=False)

	class Meta:
		db_table = 'overtime'

