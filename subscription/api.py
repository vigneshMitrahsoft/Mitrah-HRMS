from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from employee.models import employee, employee_roles,employee_type
from company.models import company, company_Settings
from .serializers import RegisterSerializer
from datetime import datetime

@api_view(('POST',))
def register(request):
	type_id = 4
	serializer = RegisterSerializer(data=request.data)
	if serializer.is_valid():
		data = serializer.validated_data
		Company = company.objects.create(
			company_name = data['company_name'],
			address = data['address'],
			created_at = datetime.now(),
			updated_at = datetime.now(),
			updated_by = 1,
			is_active = True
			)
		Company_settings=company_Settings.objects.create(
			company=Company,
			HRA = 40,
			employer_ESI = 3.25,
			employee_ESI = 0.75,
			employer_PF = 12,
			employee_PF = 12,
			leave_compensation = 1.00,
			basic_work_hours = 8.30,
			sick_leaves = 2,
			casual_leaves = 1,
			basic_pay = 100,
			other_allowances = 40,
			permission_hours = 1.5,
			pay_cycle_day = 12
			)
		Employee = employee.objects.create(
			first_name = data['first_name'],
			last_name = data['last_name'],
			email = data['email'],
			password = make_password(data['password']),
			date_of_birth = '1998/01/01',
			address = 'testing',
			date_of_joining = '2001/01/01',
			is_active = True,
			type_id = type_id,
			is_superuser = False,
			created_at = datetime.now(),
			updated_at = datetime.now(),
			created_by = 1,
			updated_by = 1 
			)
		Employee_roles = employee_roles.objects.create(
			employee_id = Employee,
			role_id = 5,
			created_at = datetime.now(),
			updated_at = datetime.now(),
			created_by = 1,
			updated_by = 1
			)
	return Response("user created successfully")
