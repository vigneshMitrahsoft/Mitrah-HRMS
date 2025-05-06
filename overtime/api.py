import datetime
import string
from django.forms import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from company.models import company_settings
from employee.models import employee
from leave.models import employee_leave_balances
from .models import Overtime
from .serializer import calculated_requested_hours, overtimeSerializer, createOvertimeSerializer, updateOvertimeSerializer, overtimeStatusUpdateSerializer
from rest_framework.exceptions import APIException
from overtime import serializer

def check_overtime_exists(pk):
	try:
		overtime = Overtime.objects.get(id = pk, is_deleted = False)
	except Overtime.DoesNotExist:
		raise APIException(detail={"statuscode": 404, "status": "error", "message": "Overtime not found"})
	return overtime

@api_view(('GET',))
def overtime_list(request):
	overtime = Overtime.objects.filter(is_deleted = False)
	serializer = overtimeSerializer(overtime, many = True)
	return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "data" : serializer.data}, status = status.HTTP_200_OK)

@api_view(('GET',))
def overtime_detail(request,pk):
	overtime = check_overtime_exists(pk)
	serializer = overtimeSerializer(overtime)
	return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "data" : serializer.data}, status = status.HTTP_200_OK)

@api_view(('POST',))
def overtime_create(request):
	employee_id = 1 #request.data.get('employee_id')
	employe = employee.objects.get(employee_id = employee_id) #request.data.get('employee_id')
	if employe is None or employe.is_active == False:
		return Response({"statuscode" : status.HTTP_400_BAD_REQUEST, "status" : "error", "message" : "Employee not found"}, status = status.HTTP_400_BAD_REQUEST)
	serializer = createOvertimeSerializer(data = request.data)
	if serializer.is_valid():
		Overtime.objects.create(**serializer.validated_data, employee_id = employe, created_by = employe.employee_id)
		return Response({"statuscode" : status.HTTP_201_CREATED, "status" : "success", "message" : "Overtime created successfully"}, status = status.HTTP_201_CREATED)
	return Response({"statuscode" : status.HTTP_400_BAD_REQUEST, "status" : "error", "message" : serializer.errors}, status = status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
def overtime_update(request, pk):
	overtime = check_overtime_exists(pk) 
	serializer = updateOvertimeSerializer(overtime, data = request.data, partial = True) 
	if serializer.is_valid():
		Overtime.objects.filter(id = pk).update(**serializer.validated_data, updated_by = 1,updated_at = datetime.datetime.now()) #request.data.get('employee_id')
		return Response({"statuscode": status.HTTP_200_OK,"status": "success","message": "Overtime updated successfully",}, status = status.HTTP_200_OK)
	else:
		return Response({"statuscode": status.HTTP_400_BAD_REQUEST,"status": "error","message": serializer.errors}, status = status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
def overtime_acceptance(request, pk):
	overtime = check_overtime_exists(pk)
	serializer = overtimeStatusUpdateSerializer(overtime, data = request.data, partial = True)
	if serializer.is_valid():
		dataz = serializer.validated_data
		
		dataz['status'] = string.capwords(dataz['status'])
		print(dataz['status'])

		if dataz['status'] not in ['Accepted', 'Rejected']:
			raise ValidationError(detail = {"statuscode" : status.HTTP_400_BAD_REQUEST, "status" : "error", "message" : "Invaild status"})
		
		if dataz['status'] == 'Accepted':
			
			requested_hours = calculated_requested_hours(overtime)
			
			employee_instance = overtime.employee_id
			company_instance = employee_instance.company_id
			company_setting_instance = company_settings.objects.filter(company = company_instance).first()

			if not company_setting_instance:
				return Response({"statuscode" : status.HTTP_400_BAD_REQUEST, "status" : "error", "message" : "Company settings not found"}, status = status.HTTP_400_BAD_REQUEST)
		
			credicted_hrs = company_setting_instance.leave_compensation * requested_hours
		
			Overtime.objects.filter(id = pk).update(status = "Accepted", credicted_hours = credicted_hrs, updated_by = 1, updated_at = datetime.datetime.now()) #request.data.get('employee_id')

			leave_balance_instance = employee_leave_balances.objects.filter(employee_id = employee_instance).first()

			if leave_balance_instance.overtime_balance_hours is None:
				leave_balance_instance.overtime_balance_hours = 0.0

			if credicted_hrs >= 8:

				leave_balance_instance.compensation_leave += 1

				remaining_hours = credicted_hrs - 8

				leave_balance_instance.overtime_balance_hours += remaining_hours
			
			elif credicted_hrs >= 4:

				leave_balance_instance.compensation_leave += 0.5

				remaining_hours = credicted_hrs - 4

				leave_balance_instance.overtime_balance_hours += remaining_hours
			
			else:
				leave_balance_instance.overtime_balance_hours += credicted_hrs

			leave_balance_instance.save()

			return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "message" : "Overtime accepted successfully"}, status = status.HTTP_200_OK)
		
		if dataz['status'] == 'Rejected':
			Overtime.objects.filter(id = pk).update(status = "Rejected", updated_by = 1, updated_at = datetime.datetime.now())	
			return  Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "message" : "Overtime rejected successfully"}, status = status.HTTP_200_OK)

	return Response({"message" : serializer.errors, "status" : "error"}, status = status.HTTP_400_BAD_REQUEST)
	

@api_view(['DELETE'])
def overtime_delete(request, pk):
	overtime = check_overtime_exists(pk)
	if overtime.is_deleted == True:
		return Response({"statuscode" : status.HTTP_400_BAD_REQUEST, "status" : "error", "message" : "Overtime already deleted"}, status = status.HTTP_400_BAD_REQUEST)
	overtime.is_deleted = True
	overtime.save()
	return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "message" : "Overtime deleted successfully"}, status = status.HTTP_200_OK)
