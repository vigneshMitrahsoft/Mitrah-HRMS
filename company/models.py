from django.db import models

# Create your models here.


class company(models.Model):
    company_id = models.BigAutoField(primary_key=True)
    company_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100)
    is_active = models.BooleanField(default= True)

    class Meta:
        db_table = 'company'


class company_settings(models.Model):
    company_settings_id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(company,on_delete=models.CASCADE)
    hra = models.FloatField(blank=True, null=True)
    employer_ESI = models.FloatField(blank=True, null=True)
    employee_ESI = models.FloatField(blank=True, null=True)
    employer_PF = models.FloatField(blank=True, null=True)
    employee_PF = models.FloatField(blank=True, null=True)
    leave_compensation = models.FloatField(blank=True, null=True)
    basic_work_hours = models.FloatField(blank=True, null=True)
    sick_leaves  = models.FloatField(blank=True, null=True)
    casual_leaves = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'company_settings' 