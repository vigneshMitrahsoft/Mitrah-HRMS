from django.db import models
import os
# Create your models here.

def upload_path(instance, filename):
	ext = filename.split('.')[-1]
	filename = f"{instance.company_id}_profile.{ext}"
	return os.path.join('company_logo/', filename)

class company(models.Model):
    company_id = models.BigAutoField(primary_key=True)
    company_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    company_logo_path = models.ImageField(upload_to = upload_path, null = True, blank = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100)
    is_active = models.BooleanField(default= True)

    class Meta:
        db_table = 'company'

class company_Settings(models.Model):
    company_settings_id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(company,on_delete=models.CASCADE, db_column = 'company_id')
    HRA = models.FloatField(blank=True, null=True, db_column = 'hra')
    basic_pay = models.FloatField(blank=True, null=True)
    other_allowances = models.FloatField(blank=True, null=True)
    employer_ESI = models.FloatField(blank=True, null=True, db_column = 'employer_esi')
    employee_ESI = models.FloatField(blank=True, null=True, db_column = 'employee_esi')
    employer_PF = models.FloatField(blank=True, null=True, db_column = 'employer_pf')
    employee_PF = models.FloatField(blank=True, null=True, db_column = 'employee_pf')
    leave_compensation = models.FloatField(blank=True, null=True)
    basic_work_hours = models.FloatField(blank=True, null=True)
    sick_leaves  = models.FloatField(blank=True, null=True)
    casual_leaves = models.FloatField(blank=True, null=True)
    permission_hours = models.FloatField(blank=True, null=True)
    pay_cycle_day = models.IntegerField(blank = True, null = True)

    class Meta:
        db_table = 'company_settings'