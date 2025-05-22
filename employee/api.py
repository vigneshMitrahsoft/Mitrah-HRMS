import glob
from django.conf import settings
from django.http import JsonResponse
from leave.models import employee_leave_balances
from .models import employee,employee_roles,roles,employee_salary_info
from taxdeduction.models import financial_year,tax_regimes,emoloyee_tax_regimes
from attendance.models import employees_attendance_info
from company.models import company_Settings,company
from holiday.models import holiday
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes,  parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .serializers import employee,get_serializer,create_serializer,employee_serializer,update_serializer,create_salary_info_serializer,get_roles
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
# from auth.permissions import HasRequiredRolesWithRoles #,CustomTokenAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.state import token_backend
from leave.serializers import create_leavebalance_serializer
from datetime import date, datetime,timedelta
from dateutil.relativedelta import relativedelta
from auth.views import IsAuthorized
import base64
import imghdr
import os
from django.db import transaction
import json

# def upload_image(id, encode_string, image_for):
# 	base64_string = encode_string
# 	try:
# 		image_data = base64.b64decode(base64_string)
# 		image_type = imghdr.what(None, image_data)
# 		allowed_types = ['jpeg', 'png','jpg']
# 		if image_type not in allowed_types:
# 			raise ValueError(f"Unsupported image type: {image_type}")
# 		directory = os.path.join("assets", "profile_picture")
# 		os.makedirs(directory, exist_ok=True)
# 		file_name = f"{id}_profile.{image_type}"
# 		file_path = os.path.join(directory, file_name)
# 		with open(file_path, "wb") as f:
# 			f.write(image_data)	
# 		for ext in allowed_types:
# 			if ext != image_type:
# 				old_file = os.path.join(directory, f"{id}_profile.{ext}")
# 				if os.path.exists(old_file):
# 					os.remove(old_file)

# 		return file_name

# 	except Exception as e:
# 		print("Error:", e)
# 		return e
	
@api_view(('GET',))
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr'])
def get_employee(request,id):
	try:
		data = employee.objects.get(employee_id = id, is_active=True)
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
@parser_classes([MultiPartParser, FormParser])
@transaction.atomic
def create_employee(request):
	data = request.data
	token_user_id = request.user.employee_id

	serializer = create_serializer(data = data)
	if not serializer.is_valid():
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	data = serializer.validated_data
	plain_password = data.get('password')
	if plain_password:
		hashed_password = make_password(plain_password)   
		data['password'] = hashed_password
	roles_data = data.pop('roles')
	# if 'profile_picture_path' in request.FILES:
	# 	data.pop('profile_picture_path')
	try:
		create_employee = employee.objects.create(**data,created_by = token_user_id, updated_by = token_user_id)

		employee_role_objs = [
			employee_roles(
				employee_id=create_employee.employee_id,
				role_id=role.role_id
			)
			for role in roles_data
		]

		employee_roles.objects.bulk_create(employee_role_objs)
		# employee_regime 
		today = date.today()
		current_year = today.year
		next_year = current_year + 1
		fy_start = date(current_year, 4, 1)
		fy_end = date(next_year, 3, 31)

		try:
			current_fy = financial_year.objects.get(start_date=fy_start, end_date=fy_end, is_active=True)
		except financial_year.DoesNotExist:
			raise ValueError("Current financial year not found or inactive")

		try:
			new_regime = tax_regimes.objects.get(regime_name="New Regime")
		except tax_regimes.DoesNotExist:
			raise ValueError("New Regime not found")

		emoloyee_tax_regimes.objects.create(
			employee_id=create_employee,
			tax_regime=new_regime,
			financial_year=current_fy,
			# selected_on=today,
			is_active=True
		)
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
			employee_leave_balances.objects.create(**data, created_by = token_user_id, updated_by = token_user_id)
		else:
			raise  ValueError(serializer.errors)

		image = data.get('profile_picture_path')
		if image:
			create_employee.profile_picture_path = image
			create_employee.save()
			create_employee.profile_picture_path.name = os.path.basename(create_employee.profile_picture_path.name)
			create_employee.save(update_fields=['profile_picture_path'])

		return Response({"statuscode":status.HTTP_201_CREATED, "status":"success", "message":"created successfully", "data": {'employee_id': create_employee.employee_id}}, status=status.HTTP_201_CREATED)
	except Exception as e:
		transaction.set_rollback(True)
		return Response({
			"status": "error",
			"message": str(e)
		}, status=status.HTTP_400_BAD_REQUEST)

@api_view(('PATCH',))
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr'])
@parser_classes([MultiPartParser, FormParser])
def update_employee(request, id):
	try:
		employee_data = employee.objects.get(employee_id = id)
	except employee.DoesNotExist:
		return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

	data = request.data
	token_user_id = request.user.employee_id

	# Profile picture will be uploaded at last, once all transactions are done
	# if 'profile_picture_path' in request.FILES:
	# 	data.pop('profile_picture_path')

	serializer = update_serializer(employee_data, data = data, partial = True)
	if serializer.is_valid():
		validated_data = serializer.validated_data

		# if 'profile_picture_path' in request.FILES:
		# 	data.pop('profile_picture_path')

		validated_role_ids = [role.role_id for role in validated_data.get('roles', [])]
		if 'roles' in validated_data:
			validated_data.pop('roles')

		employee.objects.filter(employee_id = id).update(**validated_data, updated_by = token_user_id)

		current_roles = set(
			employee_roles.objects.filter(employee_id = id, is_active = True).values_list('role_id', flat = True)
		)
		updated_roles = set(validated_role_ids)

		roles_to_deactivate = current_roles - updated_roles
		roles_to_activate_or_create = updated_roles - current_roles

		if roles_to_deactivate:
			employee_roles.objects.filter(employee_id = id, role_id__in = roles_to_deactivate).update(is_active = False)

		for role_id in roles_to_activate_or_create:
			try:
				emp_role = employee_roles.objects.get(employee_id = id, role_id = role_id)
				emp_role.is_active = True
				emp_role.updated_by = token_user_id
				emp_role.save()
			except employee_roles.DoesNotExist:
				if roles.objects.filter(role_id=role_id).exists():
					employee_roles.objects.create(
						employee_id = employee_data.employee_id,
						role_id = role_id,
						is_active = True,
						created_by = token_user_id,
						updated_by = token_user_id
					)

		image = data.get('profile_picture_path')
		if image:
			directory = os.path.join("assets", "profile_picture_path")
			previous_file_name = employee_data.profile_picture_path
			old_file = os.path.join(directory, f"{previous_file_name}")
			if os.path.exists(old_file):
				os.remove(old_file)
			employee_data.profile_picture_path = image
			employee_data.save()
			employee_data.profile_picture_path.name = os.path.basename(employee_data.profile_picture_path.name)
			employee_data.save(update_fields=['profile_picture_path'])

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
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr'])
def create_employee_salary_info(request):
	data = request.data
	serializer = create_salary_info_serializer(data = data)
	if serializer.is_valid():
		data = serializer.validated_data
		salary_info = employee_salary_info.objects.create(**data, created_by = request.user.employee_id, updated_by = request.user.employee_id)
		return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"created successfully", "data" :{"salary_id": salary_info.salary_id}},status=status.HTTP_201_CREATED)
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
		data = employee_salary_info.objects.get(employee_id = id)
	except employee_salary_info.DoesNotExist:
		return Response({"detail": "Employee salary not found"}, status=status.HTTP_404_NOT_FOUND)
	serialized_data = create_salary_info_serializer(data)
	return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)

@api_view(('GET',))
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr']) 
def get_employee_roles(request):
	data = roles.objects.all()
	serialized_data = get_roles(data,many = True)
	return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)