from django.urls import path
from . import api


urlpatterns = [
	path('<int:id>',api.generate_payslip,name='get_payslips')
]