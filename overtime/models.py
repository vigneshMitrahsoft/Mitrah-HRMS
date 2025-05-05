from django.db import models

# Create your models here.

class Overtime(models.Model):
	employee_id = models.ForeignKey("employee.Employee", on_delete=models.CASCADE, related_name="overtime")
	project_name = models.CharField(max_length=100)
	start_date = models.DateTimeField(blank= True, null=True)
	end_date = models.DateTimeField(blank= True, null=True)
	requested_hours = models.FloatField(blank=True, null=True)
	credicted_hours = models.FloatField(blank=True, null=True)
	status = models.CharField(max_length=50, blank=True, default= 'Pending')
	action = models.CharField(max_length=50, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.CharField(max_length=50, blank=True, null=True)
	updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
	updated_by = models.CharField(max_length=50, blank=True, null=True)
	is_deleted = models.BooleanField(default=False)

	class Meta:
		db_table = 'overtime'

