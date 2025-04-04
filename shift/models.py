from django.db import models
from employee.models import employee
from shifttype.models import shift_type

# Create your models here.

# class shift_type(models.Model):
#     shift_type_id = models.BigAutoField(primary_key=True)
#     shift_type_name = models.CharField(max_length=100)
#     description = models.CharField(max_length=400, blank = True)
#     is_active = models.BooleanField(default = True, blank = True)
#     created_at = models.DateTimeField(auto_now_add = True, blank = True)
#     created_by = models.IntegerField()
#     updated_at = models.DateTimeField(auto_now = True, blank = True)
#     updated_by = models.IntegerField()

#     class Meta:
#         db_table = 'shift_type'

class shift(models.Model):
    shift_id = models.BigAutoField(primary_key = True)
    shift_type_id = models.ForeignKey(shift_type, on_delete=models.DO_NOTHING, related_name = 'shifttypeid')
    start_time = models.TimeField()  # Updated to TimeField
    end_time = models.TimeField()  
    is_active = models.BooleanField(default = True)
    created_at = models.DateTimeField(auto_now_add = True)
    created_by = models.IntegerField()
    updated_at = models.DateTimeField(auto_now = True)
    updated_by = models.IntegerField()

    class Meta:
        db_table = 'shift'

class employee_shift(models.Model):
    emp_shift_id = models.BigAutoField(primary_key = True)
    emp_id = models.ForeignKey(employee, on_delete=models.DO_NOTHING, related_name = 'emp_id')
    shift_id = models.ForeignKey(shift, on_delete=models.DO_NOTHING, related_name = 'shiftid')
    shift_start_time = models.TimeField()
    shift_end_time = models.TimeField()
    is_active = models.BooleanField(default = True)
    created_at = models.DateTimeField(auto_now_add = True)
    created_by = models.IntegerField()
    updated_at = models.DateTimeField(auto_now = True)
    updated_by = models.IntegerField()

    class Meta:
        db_table = 'employee_shift'
