from django.urls import path
from . import api


urlpatterns = [
	path('<int:id>',api.get_payslip,name='get_payslip'),
	path('',api.get_all_payslips,name='get_all_payslips'),
	path('generate',api.generate_all_payslips,name='generate_all_payslips'),
	path('update/<int:id>',api.update_payslip_status,name='update_payslip_status'),
]