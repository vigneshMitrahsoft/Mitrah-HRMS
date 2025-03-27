from django.db import models

class company(models.Model):
    company_id = models.BigAutoField(primary_key=True)
    company_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100)

    class Meta:
        db_table = 'company'

class employee_role(models.Model):
    role_id = models.BigAutoField(primary_key=True)
    role_name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'employee_role'

class employee_type(models.Model):
    type_id = models.BigAutoField(primary_key=True)
    type_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'employee_type'
    
class employee(models.Model):
    employee_id = models.BigAutoField(primary_key=True)
    company_id = models.ForeignKey(company, on_delete=models.DO_NOTHING, related_name = 'companyid')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=150)
    password = models.CharField(max_length=100,default=None)
    date_of_birth = models.DateField()
    address = models.CharField(max_length=100)
    role_id = models.ForeignKey(employee_role, on_delete=models.DO_NOTHING, related_name = 'employee_roleid')
    date_of_joining = models.DateField()
    type_id = models.ForeignKey(employee_type, on_delete=models.DO_NOTHING, related_name = 'employee_typeid')
    employee_last_date = models.DateTimeField(default=None,null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.IntegerField(null=True)
    updated_by = models.IntegerField(null=True)

    class Meta:
        db_table = 'employee'

# class EmployeeAttendance(models.Model):
#     attendance_id = models.BigAutoField(primary_key=True)
#     employee_id = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, related_name = 'EmployeeAttendance')
#     date = models.DateField()
