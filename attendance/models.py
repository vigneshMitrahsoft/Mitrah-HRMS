from django.db import models
from employee.models import *

class employee_attendance(models.Model):
    attendance_id = models.BigAutoField(primary_key = True)
    employee_id = models.ForeignKey(employee, on_delete=models.DO_NOTHING, related_name = 'employeeid')
    date = models.DateField()
    check_in = models.DateTimeField()
    check_out = models.DateTimeField(null=True)
    effective_hours = models.TimeField(null = True)
    total_hours = models.TimeField(null=True)
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

class employees_attendance_info(models.Model):
    info_id = models.BigAutoField(primary_key = True)
    employee_id = models.ForeignKey(employee, on_delete=models.DO_NOTHING, related_name = 'attendanceinfo_employeeid')
    attendance_id = models.ForeignKey(employee_attendance, on_delete=models.DO_NOTHING, related_name = 'attendance_info_id')
    date = models.DateField()
    status = models.CharField(max_length = 100)
    action_by = models.IntegerField(null = True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employees_attendance_info'

class employee_applied_leaves(models.Model):
    id = models.BigAutoField(primary_key = True)
    employee_id = models.ForeignKey(employee, on_delete=models.DO_NOTHING, related_name = 'appliedleaves_employeeid')
    start_date = models.DateField()
    end_date = models.DateField()
    session = models.CharField()
    leave_type = models.CharField()
    reason = models.CharField()
    status = models.CharField() 
    action_by = models.IntegerField(null = True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employee_applied_leaves'

