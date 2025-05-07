from leave.models import employee_leave_balances
from .models import employee,employee_roles,roles,employee_salary_info
from attendance.models import employees_attendance_info
from company.models import company_Settings,company
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .serializers import employee,get_serializer,create_serializer,employee_serializer,update_serializer,create_salary_info_serializer
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
# from auth.permissions import HasRequiredRolesWithRoles #,CustomTokenAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.state import token_backend
from leave.serializers import create_leavebalance_serializer
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta

def IsAuthorized(required_roles):
	def decorator(view_func):
		def _wrapped_view(request, *args, **kwargs):
			auth_header = request.headers.get("Authorization", None)
			if not auth_header:
				return Response({"detail": "Authorization token missing"}, status=status.HTTP_401_UNAUTHORIZED)

			try:
				token = auth_header.split(" ")[1] 
				decoded_token = token_backend.decode(token)
				employee_id = decoded_token.get("employee_id")

				if not employee_id:
					return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

				employee_rolez = list(employee_roles.objects.filter(employee_id=employee_id, is_active=True).values_list("role__role_name", flat=True))

				if not employee_rolez:  
					return Response({"detail": "Employee has no assigned roles"}, status=status.HTTP_403_FORBIDDEN)

				if not any(role in employee_rolez for role in required_roles):
					return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

				return view_func(request, *args, **kwargs)
			
			except Exception as e:
				return Response({"detail": f"Authorization error: {str(e)}"}, status=status.HTTP_401_UNAUTHORIZED)
		return _wrapped_view
	return decorator

@api_view(('GET',))
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr'])
def get_employee(request,id):
	try:
		data = employee.objects.get(employee_id = id,is_active=True)
	except employee.DoesNotExist:
		return Response({"detail": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
	serialized_data = get_serializer(data)
	return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)

@api_view(('GET',))
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr']) 
def get_employees(request):
	data = employee.objects.filter(is_active=True)
	serialized_data = get_serializer(data,many = True)
	return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)

@api_view(('POST',))
def create_employee(request):
	serializer = create_serializer(data = request.data)
	if serializer.is_valid():
		data = serializer.validated_data
		plain_password = data.get('password')
		if plain_password:
			hashed_password = make_password(plain_password)   
			data['password'] = hashed_password 
		role_ids = data.pop('role_ids')
		if role_ids:
			create_employee = employee.objects.create(**data, created_by = 1, updated_by = 1)
		for role in role_ids:
			employee_roles.objects.create(employee_id = create_employee.employee_id, role_id = role.role_id)
		
		company_data = company.objects.get(company_id = request.data['company_id'])
		company_settings_data = company_Settings.objects.get(company = company_data)
		leave_balance_data = {
			'employee_id':create_employee.employee_id,
			'sick_leave':company_settings_data.sick_leaves,
			'casual_leave':company_settings_data.casual_leaves,
			'permissions':2,
			'compensation_leave': 0 
		}
		serializer = create_leavebalance_serializer(data=leave_balance_data)
		if serializer.is_valid():
			data = serializer.validated_data
			create_leave_balance = employee_leave_balances.objects.create(**data , created_by = 1, updated_by = 1)
		else:
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"created successfully"},status=status.HTTP_201_CREATED)
	else:
		print('errors', serializer.errors)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(('PATCH',))
@permission_classes((IsAuthenticated,))
def update_employee(request, id):
	data = request.data
	print(data, "data")

	try:
		employee_data = employee.objects.get(employee_id=id)
	except employee.DoesNotExist:
		return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

	serializer = update_serializer(employee_data, data=data, partial=True)

	if serializer.is_valid():
		validated_data = serializer.validated_data
		print(validated_data, "validated_data")
		serializer.save()  

		validated_role_ids = [role.role_id for role in validated_data.get('role_ids', [])]
		print("Validated Role IDs: ", validated_role_ids)

		current_roles = set(
			employee_roles.objects.filter(employee_id=id, is_active=True).values_list('role_id', flat=True)
		)
		updated_roles = set(validated_role_ids)

		roles_to_deactivate = current_roles - updated_roles
		roles_to_activate_or_create = updated_roles - current_roles
		print(roles_to_activate_or_create, "roles_to_activate_or_create")

		if roles_to_deactivate:
			employee_roles.objects.filter(employee_id=id, role_id__in=roles_to_deactivate).update(is_active=False)

		for role_id in roles_to_activate_or_create:
			print("Role ID: ", role_id)
			try:
				emp_role = employee_roles.objects.get(employee_id=id, role_id=role_id)
				emp_role.is_active = True
				emp_role.updated_by = id
				emp_role.save()
			except employee_roles.DoesNotExist:
				if roles.objects.filter(role_id=role_id).exists():
					employee_roles.objects.create(
						employee_id=employee_data.employee_id,
						role_id=role_id,
						is_active=True,
						created_by=id
					)
		return Response(
			{"statuscode": status.HTTP_200_OK, "status": "success", "message": "Updated successfully"},
			status=status.HTTP_200_OK,
		)

	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(('DELETE',))
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr'])
def delete_employee(request, id):
	employee_delete = employee.objects.get(employee_id=id)
	employee_delete.is_active = False
	employee_delete.save()
	return Response({"statuscode": status.HTTP_200_OK, "status": "success", "message": " Deleted successfully."}, status=status.HTTP_200_OK)

@api_view(('POST',))
def login(request):
	email = request.data.get('email')
	password = request.data.get('password')

	user = authenticate(request, username=email, password=password)
	if user:
		# return Response({"message": "Login successful"})
		refresh = RefreshToken.for_user(user)
		return Response({
			'access': str(refresh.access_token),
			'refresh': str(refresh),
		})
	else:   
		return Response({"message": "Invalid credentials"}, status=401)
	
@api_view(('POST',))
def create_employee_salary_info(request):
	data = request.data
	serializer = create_salary_info_serializer(data = data)
	if serializer.is_valid():
		data = serializer.validated_data
		print("data---->",data)
		salary_info = employee_salary_info.objects.create(**data, created_by = 1, updated_by =1)
		return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"created successfully"},status=status.HTTP_201_CREATED)
	else:
		print("serfdf-->",serializer.errors)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
@api_view(('PATCH',))
def update_employee_salary_info(request,id):
	salary_info = employee_salary_info.objects.get(salary_id = id)
	data = request.data
	serializer = create_salary_info_serializer(salary_info, data = data, partial = True)
	if serializer.is_valid():
		serializer.save()
		return Response(
			{"statuscode": status.HTTP_200_OK, "status": "success", "message": "Updated successfully"},
			status=status.HTTP_200_OK,
		)

	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(('GET',))
def get_employees_salary(request):
	employees_salary = employee_salary_info.objects.all()
	serialized_data = create_salary_info_serializer(employees_salary, many=True)
	return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)

@api_view(('GET',))
def get_employee_salary(request,id):
	try:
		data = employee_salary_info.objects.get(salary_id = id)
	except employee_salary_info.DoesNotExist:
		return Response({"detail": "Employee salary not found"}, status=status.HTTP_404_NOT_FOUND)
	serialized_data = create_salary_info_serializer(data)
	return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)

@api_view(('GET',))
def calculate_employee_salary(request,id):
	pass
	employee_instance = employee.objects.get(employee_id = id)
	# company_instance = company.objects.get(company_id = employee_instance.company_id.company_id)
	employee_company = company_Settings.objects.get(company = employee_instance.company_id.company_id)
	print("dfff-->",employee_company.employee_PF,employee_company.employee_ESI)
	employee_salary = employee_salary_info.objects.get(employee_id = employee_instance)
	ctc = employee_salary.gross_salary + employee_salary.variable_pay
	print(ctc,"ctc")
	basic_pay = ctc*0.4
	hra = ctc*0.2
	other_allowance = ctc*0.4
	print("hra-->",hra)
	print("hra-->",other_allowance)
	employee_pf = employee_company.employee_PF
	employee_esi = employee_company.employee_ESI
	print("basic pay-->",basic_pay)
	employee_pf_deduction = (employee_pf/100) * basic_pay
	employee_esi_deduction = (employee_esi/100)* employee_salary.gross_salary
	print("employ--->",employee_pf_deduction,employee_esi_deduction)
	
	input_str = "07-05-2025"
	given_date = datetime.strptime(input_str, "%d-%m-%Y").date()
	start_date = given_date - relativedelta(months=1)
	end_date = given_date
	# total_days_of_month = (end_date - start_date).days
	# print("total month--->",total_days_of_month)
	weekday_count = 0
	current_date = start_date
	while current_date <= end_date:
		if current_date.weekday() < 5: 
			weekday_count += 1
		current_date += timedelta(days=1)
	print("weekend_count---->",weekday_count)
	start_date = start_date.strftime("%Y-%m-%d")
	end_date = end_date.strftime("%Y-%m-%d")

	leave_dates = employees_attendance_info.objects.filter(date__range = [start_date,end_date],status = 'Absent')
	holiday_leave = 2

	total_working_day_of_month = weekday_count-holiday_leave
	employee_working_day = total_working_day_of_month
	employee_lop = (employee_salary.gross_salary / total_working_day_of_month)* 1.5
	print("employee_lop-->",employee_lop)
	deduction = employee_esi_deduction + employee_pf_deduction + employee_lop
	print("ded-->",deduction)
	net_salary = (basic_pay + hra + other_allowance) - deduction
	print("net_salary--->",net_salary)




