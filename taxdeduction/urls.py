from django.urls import path
from . import api

urlpatterns = [
	path('create_fy_regimes',api.setup_financial_year_and_regimes, name='setup_financial_year_and_regimes'),
	path('create_tax_slabs', api.setup_tax_slabs, name='setup_tax_slabs'),
	# path('',api.calculate_employee_tax_deduction, name='calculate_employee_tax_deduction'),
	
]