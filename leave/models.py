from django.db import models
from employee.models import employee

class employee_applied_leaves(models.Model):
	id = models.BigAutoField(primary_key = True)

	employee_id = models.ForeignKey(employee, on_delete=models.DO_NOTHING, related_name = 'appliedleaves_employeeid', db_column = 'employee_id')
	start_date = models.DateField()
	end_date = models.DateField()
	leave_type = models.CharField()
	reason = models.CharField()
	status = models.CharField() 
	action_by = models.IntegerField(null = True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'employee_applied_leaves'

class employee_leave_balances(models.Model):
	leave_balance_id  = models.AutoField(primary_key=True)
	employee_id  = models.OneToOneField(employee, on_delete=models.DO_NOTHING, related_name = 'employee_leavebalanceid')
	sick_leave = models.FloatField(default=0)
	casual_leave = models.FloatField(default=0)
	permissions = models.TimeField(default=0)
	compensation_leave = models.FloatField(default=0)
	overtime_balance_hours = models.FloatField(default=0, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	created_by = models.IntegerField(null=True)
	updated_by = models.IntegerField(null=True)
	
	class Meta:
		db_table = 'employee_leave_balances'

class employee_applied_leave_days(models.Model):
	leave_days_id = models.AutoField(primary_key = True)

	applied_leave_request_id  = models.ForeignKey(employee_applied_leaves, on_delete=models.DO_NOTHING, related_name ='leave_days', db_column = 'applied_leave_request_id')
	leave_date = models.DateField()
	session = models.CharField(max_length = 100)
	comment = models.CharField (max_length = 200)
	status = models.CharField(max_length = 100)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	created_by = models.IntegerField(null=True)
	updated_by = models.IntegerField(null=True)

	class Meta:
		db_table = 'employee_applied_leave_days'

class employee_applied_permissions(models.Model):
	permission_id = models.BigAutoField(primary_key=True)

	employee = models.ForeignKey(employee, on_delete=models.DO_NOTHING, related_name = 'emp_permission', db_column = 'employee_id')
	permission_date = models.DateField()
	start_time = models.TimeField()
	end_time = models.TimeField()
	reason = models.CharField(null=True , blank=True)
	status = models.CharField(default = "Pending")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	created_by = models.IntegerField(null=True)
	updated_by = models.IntegerField(null=True)

	class Meta:
		db_table = 'employee_applied_permissions'