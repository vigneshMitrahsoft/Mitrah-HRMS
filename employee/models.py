from django.db import models

class Company(models.Model):
    company_id = models.BigAutoField(primary_key=True)
    company_name = models.CharField(max_length=100)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100)

    class Meta:
        db_table = 'company'

class EmployeeRole(models.Model):
    role_id = models.BigAutoField(primary_key=True)
    role_name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'employee_role'

class EmployeeType(models.Model):
    type_id = models.BigAutoField(primary_key=True)
    type_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'employee_type'
    
class Employee(models.Model):
    employee_id = models.BigAutoField(primary_key=True)
    company_id = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name = 'Company')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    password = models.TextField(null=True)
    date_of_birth = models.DateField()
    address = models.TextField()
    role_id = models.ForeignKey(EmployeeRole, on_delete=models.DO_NOTHING, related_name = 'EmployeeRole')
    date_of_joining = models.DateTimeField()
    type_id = models.ForeignKey(EmployeeType, on_delete=models.DO_NOTHING, related_name = 'EmployeeType')
    employee_last_date = models.DateTimeField(default=None,null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100)
    updated_by = models.CharField(max_length=100)

    class Meta:
        db_table = 'employee'

# class EmployeeAttendance(models.Model):
#     attendance_id = models.BigAutoField(primary_key=True)
#     employee_id = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, related_name = 'EmployeeAttendance')
#     date = models.DateField()
