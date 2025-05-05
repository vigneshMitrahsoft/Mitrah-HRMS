from django.db import models
from employee.models import employee
from attendance.models import employee_applied_leaves

class employee_leave_balances(models.Model):
    leave_balance_id  = models.AutoField(primary_key=True)
    employee_id  = models.OneToOneField(employee, on_delete=models.DO_NOTHING, related_name = 'employee_leavebalanceid')
    sick_leave = models.FloatField(default=0)
    casual_leave = models.FloatField(default=0)
    permissions = models.FloatField(default=0)
    compensation_leave = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.IntegerField(null=True)
    updated_by = models.IntegerField(null=True)
    
    class Meta:
        db_table = 'employee_leave_balances'

class employee_applied_leave_days(models.Model):
    leave_days_id = models.AutoField(primary_key = True)
    applied_leave_request_id  = models.ForeignKey(employee_applied_leaves, on_delete=models.DO_NOTHING, related_name ='leave_days')
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


    
