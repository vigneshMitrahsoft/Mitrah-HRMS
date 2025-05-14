from django.db import models
from django.utils import timezone
from employee.models import employee

# Create your models here.


class LoanDeduction(models.Model):
	loan_id = models.AutoField(primary_key=True)
	employee = models.ForeignKey(employee, on_delete=models.CASCADE, default= 1)
	# employee_id = models.ForeignKey(blank=True, null=True)
	loan_type = models.CharField(max_length=100)
	loan_amount = models.FloatField(blank=True)
	requested_date = models.DateTimeField(default=timezone.now)
	approved_date = models.DateTimeField(blank=True, null=True)
	reasons = models.CharField(blank=True, null=True)
	repayment_type = models.CharField(max_length=100,blank=True, null=True)
	start_date = models.DateTimeField(blank=True, null=True)
	end_date = models.DateTimeField(blank=True, null=True)
	percentage_amount = models.FloatField(blank=True, null=True)
	fixed_amount = models.FloatField(blank=True, null=True)
	tenure = models.FloatField(blank=True, null=True)
	status = models.CharField(max_length=50, blank=True, default= 'Pending')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
	is_deleted = models.BooleanField(default=False)

	class Meta:
		db_table = 'loans'



class Repayment(models.Model):
	repayment_id = models.AutoField(primary_key=True)
	loan = models.ForeignKey(LoanDeduction, on_delete=models.CASCADE)
	payment_date = models.DateTimeField(blank=True, null=True)
	amount_paid = models.FloatField(blank=True)
	remaining_balance = models.FloatField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)

	class Meta:
		db_table = 'repayments'
		

class EmiRepayments(models.Model):
	loan = models.ForeignKey(LoanDeduction, on_delete=models.CASCADE)
	payment_date = models.DateTimeField(blank=True, null=True)
	amount = models.FloatField(blank=True)
	remaining_balance = models.FloatField(blank=True)
	status = models.CharField(max_length=50, blank=True, default= 'upcoming')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
	
	class Meta:
		db_table = 'emi_repayments'