import datetime
import string
from django.forms import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from company.models import company_Settings
from employee.models import employee
from leave.models import employee_leave_balances
from .models import Overtime
from .serializer import calculated_requested_hours, overtimeSerializer, createOvertimeSerializer, updateOvertimeSerializer, overtimeStatusUpdateSerializer
from rest_framework.exceptions import APIException
from overtime import serializer
from rest_framework.permissions import IsAuthenticated

def check_overtime_exists(pk):
	try:
		overtime = Overtime.objects.get(id = pk, is_deleted = False)
	except Overtime.DoesNotExist:
		raise APIException(detail={"statuscode": 404, "status": "error", "message": "Overtime not found"})
	return overtime

def check_employee_exists(employee_id):
	try:
		employee_instance = employee.objects.get(employee_id = employee_id, is_active = True)
	except employee.DoesNotExist:
		raise APIException(detail={"statuscode": 404, "status": "error", "message": "Employee not found"})
	return employee_instance

@api_view(('GET',))
@permission_classes((IsAuthenticated,))
def overtime_list(request):
	overtime = Overtime.objects.filter(is_deleted = False)
	serializer = overtimeSerializer(overtime, many = True)
	return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "data" : serializer.data}, status = status.HTTP_200_OK)

@api_view(('GET',))
@permission_classes((IsAuthenticated,))
def overtime_detail(request,pk):
	overtime = check_overtime_exists(pk)
	serializer = overtimeSerializer(overtime)
	return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "data" : serializer.data}, status = status.HTTP_200_OK)

@api_view(('POST',))
@permission_classes((IsAuthenticated,))
def overtime_create(request):
	employee_id = request.user.employee_id
	employe = check_employee_exists(employee_id)
	serializer = createOvertimeSerializer(data = request.data, context = {'employee' : employe})
	if serializer.is_valid():
		Overtime.objects.create(**serializer.validated_data, employee_id = employe, created_by = employe.employee_id)
		return Response({"statuscode" : status.HTTP_201_CREATED, "status" : "success", "message" : "Overtime created successfully"}, status = status.HTTP_201_CREATED)
	return Response({"statuscode" : status.HTTP_400_BAD_REQUEST, "status" : "error", "message" : serializer.errors}, status = status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes((IsAuthenticated,))
def overtime_update(request, pk):
	employee_id = request.user.employee_id
	employe = check_employee_exists(employee_id)
	overtime = check_overtime_exists(pk) 
	serializer = updateOvertimeSerializer(overtime, data = request.data, partial = True, context = {'employee' : employe}) 
	if serializer.is_valid():
		Overtime.objects.filter(id = pk).update(**serializer.validated_data, updated_by = employee_id, updated_at = datetime.datetime.now()) 
		return Response({"statuscode": status.HTTP_200_OK,"status": "success","message": "Overtime updated successfully",}, status = status.HTTP_200_OK)
	else:
		return Response({"statuscode": status.HTTP_400_BAD_REQUEST,"status": "error","message": serializer.errors}, status = status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes((IsAuthenticated,))
def overtime_acceptance(request, pk):
	employee_id = request.user.employee_id
	employe = check_employee_exists(employee_id)
	overtime = check_overtime_exists(pk)
	serializer = overtimeStatusUpdateSerializer(overtime, data = request.data, partial = True)
	if serializer.is_valid():
		datas = serializer.validated_data
		
		datas['status'] = string.capwords(datas['status'])

		if datas['status'] not in ['Accepted', 'Rejected']:
			raise ValidationError(detail = {"statuscode" : status.HTTP_400_BAD_REQUEST, "status" : "error", "message" : "Invaild status"})
		
		if datas['status'] == 'Accepted':
			requested_hours = calculated_requested_hours(overtime)
			employee_instance = overtime.employee_id
			company_instance = employee_instance.company_id
			company_setting_instance = company_Settings.objects.filter(company = company_instance).first()

			if not company_setting_instance:
				return Response({"statuscode" : status.HTTP_400_BAD_REQUEST, "status" : "error", "message" : "Company settings not found"}, status = status.HTTP_400_BAD_REQUEST)
			credited_hrs = company_setting_instance.leave_compensation * requested_hours
			Overtime.objects.filter(id = pk).update(status = "Accepted", credited_hours = credited_hrs, updated_by = employe.employee_id, updated_at = datetime.datetime.now()) #request.data.get('employee_id')
			leave_balance_instance = employee_leave_balances.objects.filter(employee_id = employee_instance).first()

			if leave_balance_instance.overtime_balance_hours is None:
				leave_balance_instance.overtime_balance_hours = 0.0
			if credited_hrs >= 8:
				leave_balance_instance.compensation_leave += 1
				remaining_hours = credited_hrs - 8
				leave_balance_instance.overtime_balance_hours += remaining_hours
			elif credited_hrs >= 4:
				leave_balance_instance.compensation_leave += 0.5
				remaining_hours = credited_hrs - 4
				leave_balance_instance.overtime_balance_hours += remaining_hours
			else:
				leave_balance_instance.overtime_balance_hours += credited_hrs
			leave_balance_instance.save()
			return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "message" : "Overtime accepted successfully"}, status = status.HTTP_200_OK)
		if datas['status'] == 'Rejected':
			Overtime.objects.filter(id = pk).update(status = "Rejected", updated_by = employe.employee_id, updated_at = datetime.datetime.now())	
			return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "message" : "Overtime rejected successfully"}, status = status.HTTP_200_OK)
	return Response({"message" : serializer.errors, "status" : "error"}, status = status.HTTP_400_BAD_REQUEST)
	

@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def overtime_delete(request, pk):
	employee_id = request.user.employee_id
	employe = check_employee_exists(employee_id)
	overtime = check_overtime_exists(pk)
	if overtime.is_deleted == True:
		return Response({"statuscode" : status.HTTP_400_BAD_REQUEST, "status" : "error", "message" : "Overtime already deleted"}, status = status.HTTP_400_BAD_REQUEST)
	overtime.is_deleted = True
	overtime.updated_by = employe.employee_id
	overtime.updated_at = datetime.datetime.now()
	overtime.save()
	return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "message" : "Overtime deleted successfully"}, status = status.HTTP_200_OK)
