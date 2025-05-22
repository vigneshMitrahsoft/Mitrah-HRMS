from django.db import models
from employee.models import employee

# Create your models here.

class financial_year(models.Model):
	financial_year_id = models.BigAutoField(primary_key=True)
	year_label = models.CharField(max_length=30)
	start_date = models.DateField()
	end_date = models.DateField()
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	created_by = models.IntegerField(blank=True, null=True)
	updated_by = models.IntegerField(blank=True, null=True)

	class Meta:
		db_table = 'financial_year'

class tax_regimes(models.Model):
	tax_regime_id = models.BigAutoField(primary_key=True)
	regime_name = models.CharField(max_length=100)  # 'Old Regime' or 'New Regime'
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	created_by = models.IntegerField(blank=True, null=True)
	updated_by = models.IntegerField(blank=True, null=True)

	class Meta:
		db_table = 'tax_regimes'


class tax_slabs(models.Model):
	tax_slab_id = models.BigAutoField(primary_key=True)
	financial_year = models.ForeignKey(financial_year, on_delete=models.CASCADE, db_column='financial_year_id')
	tax_regime = models.ForeignKey(tax_regimes, on_delete=models.CASCADE, db_column='tax_regime_id')
	slab_from = models.DecimalField(max_digits=12, decimal_places=2)
	slab_to = models.DecimalField(max_digits=12, decimal_places=2)
	slab_rate = models.DecimalField(max_digits=5, decimal_places=2)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	created_by = models.IntegerField(blank=True, null=True)
	updated_by = models.IntegerField(blank=True, null=True)

	class Meta:
		db_table = 'tax_slabs'


class employee_tax_regimes(models.Model):
	employee_tax_regime_id = models.BigAutoField(primary_key=True)
	employee_id = models.ForeignKey(employee, on_delete=models.CASCADE, db_column='employee_id')
	financial_year = models.ForeignKey(financial_year, on_delete=models.CASCADE, db_column='financial_year_id')
	tax_regime = models.ForeignKey(tax_regimes, on_delete=models.CASCADE, db_column='tax_regime_id', default=2)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	created_by = models.IntegerField(blank=True, null=True)
	updated_by = models.IntegerField(blank=True, null=True)

	class Meta:
		db_table = 'employee_tax_regimes'