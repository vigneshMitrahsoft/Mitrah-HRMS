from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from employee.models import employee
from .models import Overtime
from .serializer import overtimeSerializer, createOvertimeSerializer, updateOvertimeSerializer
from rest_framework.exceptions import APIException

def check_overtime_exists(pk):
	try:
		overtime = Overtime.objects.get(id = pk, is_deleted = False)
	except Overtime.DoesNotExist:
		raise APIException(detail={"statuscode": 404, "status": "error", "message": "Overtime not found"})
	return overtime

@api_view(('GET',))
def overtime_list(request):
	overtime = Overtime.objects.filter(is_deleted = False)
	serializer = overtimeSerializer(overtime, many=True)
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
	print("employe", employe)
	if employe is None or employe.is_active == False:
		return Response({"statuscode" : status.HTTP_400_BAD_REQUEST, "status" : "error", "message" : "Employee not found"}, status = status.HTTP_400_BAD_REQUEST)
	serializer = createOvertimeSerializer(data=request.data)
	if serializer.is_valid():
		Overtime.objects.create(**serializer.validated_data, employee_id = employe, created_by = employe.employee_id)
		return Response({"statuscode" : status.HTTP_201_CREATED, "status" : "success", "message" : "Overtime created successfully"}, status = status.HTTP_201_CREATED)
	return Response({"statuscode" : status.HTTP_400_BAD_REQUEST, "status" : "error", "message" : serializer.errors}, status = status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
def overtime_update(request, pk):
	overtime = check_overtime_exists(pk) 
	serializer = updateOvertimeSerializer(overtime, data=request.data, partial=True) 
	if serializer.is_valid():
		Overtime.objects.filter(id = pk).update(**serializer.validated_data, updated_by = 1) #request.data.get('employee_id')
		return Response({"statuscode": status.HTTP_200_OK,"status": "success","message": "Overtime updated successfully","data": serializer.data}, status=status.HTTP_200_OK)
	else:
		return Response({"statuscode": status.HTTP_400_BAD_REQUEST,"status": "error","message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def overtime_delete(request, pk):
	overtime = check_overtime_exists(pk)
	if overtime.is_deleted == True:
		return Response({"statuscode" : status.HTTP_400_BAD_REQUEST, "status" : "error", "message" : "Overtime already deleted"}, status = status.HTTP_400_BAD_REQUEST)
	overtime.is_deleted = True
	overtime.save()
	return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "message" : "Overtime deleted successfully"}, status = status.HTTP_200_OK)
