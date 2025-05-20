from django.db import models
from employee.models import employee


# Create your models here.

class Payslip(models.Model):
	payslip_id = models.AutoField(primary_key=True)
	employee = models.ForeignKey(employee, on_delete=models.CASCADE, db_column = 'employee_id')
	month = models.CharField(max_length=20)
	year = models.IntegerField(blank=True, null=True)
	basic_pay = models.FloatField(blank=True, null=True)
	hra = models.FloatField(blank=True, null=True)
	other_allowances = models.FloatField(blank=True, null=True)
	travel_allowance = models.FloatField(blank=True, null=True)
	employee_pf = models.FloatField(blank=True, null=True)
	employee_esi = models.FloatField(blank=True, null=True)
	employer_pf = models.FloatField(blank=True, null=True)
	employer_esi = models.FloatField(blank=True, null=True)
	loan_emi = models.FloatField(blank=True, null=True)
	lop = models.FloatField(blank=True, null=True)
	tax_deduction = models.FloatField(blank=True, null=True)
	net_pay = models.FloatField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	updated_by = models.IntegerField(blank=True, null=True)
	status = models.CharField(max_length=20, default='pending')
	class Meta:
		db_table = 'payslips'