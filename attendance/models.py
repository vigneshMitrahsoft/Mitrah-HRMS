from django.db import models
from employee.models import *

class employee_attendance(models.Model):
    attendance_id = models.BigAutoField(primary_key = True)
    employee_id = models.ForeignKey(employee, on_delete=models.DO_NOTHING, related_name = 'employeeid')
    date = models.DateField()
    check_in = models.DateTimeField()
    check_out = models.DateTimeField(null=True)
    effective_hours = models.FloatField(null = True)
    total_hours = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(null=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.IntegerField(null=True)

    class Meta:
        db_table = 'employee_attendance'

class attendance_entries(models.Model):
    entry_id = models.BigAutoField(primary_key = True)
    attendance_id = models.ForeignKey(employee_attendance, on_delete=models.DO_NOTHING, related_name = 'attendanceid')
    checkin_entry = models.DateTimeField()
    checkout_entry = models.DateTimeField(null = True)

    class Meta:
        db_table = 'attendance_entries'


