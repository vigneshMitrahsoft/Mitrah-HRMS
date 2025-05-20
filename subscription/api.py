from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from employee.models import employee, employee_roles
from company.models import company, company_Settings
from .serializers import RegisterSerializer

@api_view(('POST',))
def register(request):
	request.data['type_id'] = 4
	serializer = RegisterSerializer(data=request.data)
	if not serializer.is_valid():
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	data = serializer.validated_data
	company_model = company.objects.create(
			company_name = data['company_name'],
			address = data['address'],
			is_active = True
	)
	company_Settings.objects.create(
		company = company_model,
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
		
	employee_model = employee.objects.create(
		company_id = company_model,
		first_name = data['first_name'],
		last_name = data['last_name'],
		email = data['email'],
		password = make_password(data['password']),
		date_of_birth = '1998-01-01',
		address = 'testing',
		date_of_joining = '2001-01-01',
		is_active = True,
		is_superuser = False,
		type_id=data['type_id'],
	)

	employee_roles.objects.bulk_create([
	employee_roles(employee_id = employee_model.employee_id, role_id = 5),
	employee_roles(employee_id = employee_model.employee_id, role_id = 6)
	])

	return Response({"statuscode":status.HTTP_201_CREATED,"status":"success" ,"message":"Registered successfully"},status=status.HTTP_201_CREATED)
