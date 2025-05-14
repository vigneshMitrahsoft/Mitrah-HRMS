from django.http import JsonResponse
from leave.models import employee_leave_balances
from .models import employee,employee_roles,roles,employee_salary_info
from attendance.models import employees_attendance_info
from company.models import company_Settings,company
from holiday.models import holiday
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
from auth.views import IsAuthorized
import base64
import imghdr
import os

def upload_image(id, encode_string, image_for):
	base64_string = encode_string
	try:
		image_data = base64.b64decode(base64_string)
		image_type = imghdr.what(None, image_data)
		allowed_types = ['jpeg', 'png','jpg']
		if image_type not in allowed_types:
			raise ValueError(f"Unsupported image type: {image_type}")
		directory = os.path.join("assets", "profile_picture")
		os.makedirs(directory, exist_ok=True)
		file_name = f"{id}_profile.{image_type}"
		file_path = os.path.join(directory, file_name)
		with open(file_path, "wb") as f:
			f.write(image_data)	
		for ext in allowed_types:
			if ext != image_type:
				old_file = os.path.join(directory, f"{id}_profile.{ext}")
				if os.path.exists(old_file):
					os.remove(old_file)

		return file_name

	except Exception as e:
		print("Error:", e)
		return e


@api_view(('GET',))
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr'])
def get_employee(request,id):
	try:
		data = employee.objects.get(employee_id = id,is_active=True)
	except employee.DoesNotExist:
		return Response({"detail": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

	serialized_data = get_serializer(data, context = {'request': request})
	return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)
@api_view(('GET',))
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr']) 
def get_employees(request):
	data = employee.objects.filter(is_active=True)
	serialized_data = get_serializer(data,many = True, context = {'request': request})
	return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)

@api_view(('POST',))
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr'])
def create_employee(request):
	data = request.data
	token_user_id = request.user.employee_id
	serializer = create_serializer(data = data)
	if serializer.is_valid():
		data = serializer.validated_data
		plain_password = data.get('password')
		if plain_password:
			hashed_password = make_password(plain_password)   
			data['password'] = hashed_password
		role_ids = data.pop('role_ids')
		if role_ids:
			create_employee = employee.objects.create(**data, created_by = token_user_id, updated_by = token_user_id)
			if 'profile_picture' in request.data:
				encode_string = request.data['profile_picture']
				employee_id = create_employee.employee_id
				profile_picture_path = upload_image(employee_id, encode_string, image_for = 'employee')
				create_employee.profile_picture_path = profile_picture_path
				create_employee.save()
		for role in role_ids:
			employee_roles.objects.create(employee_id = create_employee.employee_id, role_id = role.role_id)
		
		company_data = company.objects.get(company_id = request.data['company_id'])
		company_settings_data = company_Settings.objects.get(company = company_data)
		leave_balance_data = {
			'employee_id':create_employee.employee_id,
			'sick_leave':company_settings_data.sick_leaves,
			'casual_leave':company_settings_data.casual_leaves,
			'permission_hours':company_settings_data.permission_hours,
			'compensation_leave': company_settings_data.leave_compensation
		}
		serializer = create_leavebalance_serializer(data=leave_balance_data)
		if serializer.is_valid():
			data = serializer.validated_data
			create_leave_balance = employee_leave_balances.objects.create(**data , created_by = token_user_id, updated_by = token_user_id)
		else:
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"created successfully"},status=status.HTTP_201_CREATED)
	else:
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(('PATCH',))
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr'])
def update_employee(request, id):
	data = request.data
	token_user_id = request.user.employee_id
	try:
		employee_data = employee.objects.get(employee_id=id)
	except employee.DoesNotExist:
		return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
	if 'profile_picture' in request.data:
		encode_string = request.data['profile_picture']
		employee_id = employee_data.employee_id
		profile_picture_path = upload_image(employee_id, encode_string, image_for = 'employee')
		data['profile_picture_path'] = profile_picture_path

	serializer = update_serializer(employee_data, data=data, partial=True)
	if serializer.is_valid():
		
		validated_data = serializer.validated_data
		serializer.save(updated_by = token_user_id)  
 
		validated_role_ids = [role.role_id for role in validated_data.get('role_ids', [])]

		current_roles = set(
			employee_roles.objects.filter(employee_id=id, is_active=True).values_list('role_id', flat=True)
		)
		updated_roles = set(validated_role_ids)

		roles_to_deactivate = current_roles - updated_roles
		roles_to_activate_or_create = updated_roles - current_roles

		if roles_to_deactivate:
			employee_roles.objects.filter(employee_id=id, role_id__in=roles_to_deactivate).update(is_active=False)

		for role_id in roles_to_activate_or_create:
			try:
				emp_role = employee_roles.objects.get(employee_id=id, role_id=role_id)
				emp_role.is_active = True
				emp_role.updated_by = token_user_id
				emp_role.save()
			except employee_roles.DoesNotExist:
				if roles.objects.filter(role_id=role_id).exists():
					employee_roles.objects.create(
						employee_id=employee_data.employee_id,
						role_id=role_id,
						is_active=True,
						created_by=token_user_id,
						updated_by = token_user_id
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
	employee_delete.updated_by = request.user.employee_id
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
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr'])
def create_employee_salary_info(request):
	data = request.data
	serializer = create_salary_info_serializer(data = data)
	if serializer.is_valid():
		data = serializer.validated_data
		salary_info = employee_salary_info.objects.create(**data, created_by = request.user.employee_id, updated_by = request.user.employee_id)
		return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"created successfully"},status=status.HTTP_201_CREATED)
	else:
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
@api_view(('PATCH',))
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr'])
def update_employee_salary_info(request,id):
	salary_info = employee_salary_info.objects.get(salary_id = id)
	data = request.data
	serializer = create_salary_info_serializer(salary_info, data = data, partial = True)
	if serializer.is_valid():
		serializer.save(updated_by = request.user.employee_id)
		return Response(
			{"statuscode": status.HTTP_200_OK, "status": "success", "message": "Updated successfully"},
			status=status.HTTP_200_OK,
		)

	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(('GET',))
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr'])
def get_employees_salary(request):
	employees_salary = employee_salary_info.objects.all()
	serialized_data = create_salary_info_serializer(employees_salary, many=True)
	return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)

@api_view(('GET',))
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr'])
def get_employee_salary(request,id):
	try:
		data = employee_salary_info.objects.get(salary_id = id)
	except employee_salary_info.DoesNotExist:
		return Response({"detail": "Employee salary not found"}, status=status.HTTP_404_NOT_FOUND)
	serialized_data = create_salary_info_serializer(data)
	return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)

@api_view(('GET',))
def calculate_employee_salary(request,id):
	employee_instance = employee.objects.get(employee_id = id)
	# company_instance = company.objects.get(company_id = employee_instance.company_id.company_id)
	employee_company = company_Settings.objects.get(company = employee_instance.company_id.company_id)
	employee_salary = employee_salary_info.objects.get(employee_id = employee_instance)
	ctc = employee_salary.gross_salary + employee_salary.variable_pay
	basic_pay = ctc*(employee_company.basic_pay / 100)
	hra = basic_pay*(employee_company.HRA / 100)
	other_allowance = basic_pay*(employee_company.other_allowances / 100)
	employee_pf = employee_company.employee_PF
	employee_esi = employee_company.employee_ESI
	employee_pf_deduction = (employee_pf/100) * basic_pay
	employee_esi_deduction = (employee_esi/100)* employee_salary.gross_salary
	company_audit_date = "31"  #TODO: need to get the value from company_settings
	today = datetime.today()
	month = today.month
	year = today.year
	date = str(company_audit_date) + "-" + str(month) + "-" + str(year)
	given_date = datetime.strptime(date, "%d-%m-%Y").date()
	start_date = given_date - relativedelta(months=1)
	end_date = given_date
	weekday_count = 0
	current_date = start_date
	while current_date <= end_date:
		if current_date.weekday() < 5: 
			weekday_count += 1
		current_date += timedelta(days=1)
	start_date = start_date.strftime("%Y-%m-%d")
	end_date = end_date.strftime("%Y-%m-%d")
	leave_dates = employees_attendance_info.objects.filter(date__range = [start_date,end_date],status = 'Absent')
	company_holidays = holiday.objects.filter(holiday_date__range = [start_date, end_date])
	total_working_day_of_month = weekday_count - len(company_holidays)
	employee_working_day = total_working_day_of_month
	employee_lop = (employee_salary.gross_salary / total_working_day_of_month) * len(leave_dates)
	deduction = employee_esi_deduction + employee_pf_deduction + employee_lop
	net_salary = (basic_pay + hra + other_allowance) - deduction