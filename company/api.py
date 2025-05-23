from datetime import datetime
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from .models import company, company_Settings
from .serializers import companySerializer, companyCreateSerializer, companyUpdateSerializer
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import os

def check_company_exists(pk):
	try:
		comp = company.objects.filter(company_id = pk, is_active = True)
	except company.DoesNotExist:
		return Response ({"details" : "company not found"}, status = status.HTTP_404_NOT_FOUND)
	return comp

@api_view(('GET',))
def company_list(request):
	companies = company.objects.filter(is_active = True)
	serializer = companySerializer(companies, many = True, context = {'request': request})
	return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "data" : serializer.data}, status = status.HTTP_200_OK)

@api_view(('GET',))
def specific_company(request, pk):
	comp = company.objects.get(company_id = pk)
	serializer = companySerializer(comp, context = {'request': request})
	return Response ({"statuscode" : status.HTTP_200_OK, "status" : "success", "data" : serializer.data}, status = status.HTTP_200_OK)

@parser_classes([MultiPartParser, FormParser])
@api_view(('POST',))
@transaction.atomic
def company_create(request):
	serializer = companyCreateSerializer(data = request.data)
	if not serializer.is_valid():
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	else:
		data = serializer.validated_data
		try:
			comp = company.objects.create(company_name = data['company_name'], address = data['address'],created_at = datetime.now())
			image = data.get('company_logo_path')
			if image:
				comp.company_logo_path = image
				comp.save()
				comp.company_logo_path.name = os.path.basename(comp.company_logo_path.name)
				comp.save(update_fields=['company_logo_path'])

			company_Settings.objects.create(
				company = comp,
				HRA = data['hra'],
				employer_ESI = data['employer_ESI'],
				employee_ESI = data['employee_ESI'], 
				employer_PF = data['employer_PF'],
				employee_PF = data['employee_PF'],
				leave_compensation = data['leave_compensation'],
				basic_work_hours = data['basic_work_hours'],
				sick_leaves = data['sick_leaves'],
				casual_leaves = data['casual_leaves'],
				basic_pay = data['basic_pay'],
				other_allowances = data['other_allowances'],
				permission_hours = data['permission_hours'],
				pay_cycle_day = data['pay_cycle_day']
			)
			return Response({"statuscode" : status.HTTP_201_CREATED, "status" : "success", "message" : "company created successfully"}, status = status.HTTP_201_CREATED)
		except Exception as e:
			transaction.set_rollback(True)
			return Response({
				"status": "error",
				"message": str(e)
			}, status=status.HTTP_400_BAD_REQUEST)

@parser_classes([MultiPartParser, FormParser])
@api_view(('PATCH',))
def company_update(request,pk):
	comp = check_company_exists(pk)
	serializer = companyUpdateSerializer(comp, data = request.data, partial = True)
	if serializer.is_valid():
		data = serializer.validated_data
		comp = company.objects.get(company_id=pk)
		comp.company_name = data.get('company_name', comp.company_name)
		comp.address = data.get('address', comp.address)
		comp.updated_at = datetime.now()
		
		image = data.get('company_logo_path')
		if image:
			directory = os.path.join("assets", "company_logo")
			previous_file_name = comp.company_logo_path if comp.company_logo_path else None
			if previous_file_name:
				old_file = os.path.join(directory, f"{previous_file_name}")
				if os.path.isfile(old_file):
					os.remove(old_file)
			comp.company_logo_path = image
			comp.save()
			comp.company_logo_path.name = os.path.basename(comp.company_logo_path.name)
			comp.save(update_fields=['company_logo_path'])
			
			company_Settings.objects.filter(company_id=pk).update(
				HRA=data['hra'],
				employer_ESI=data['employer_ESI'],
				employee_ESI=data['employee_ESI'],
				employer_PF=data['employer_PF'],
				employee_PF=data['employee_PF'],
				leave_compensation=data['leave_compensation'],
				basic_work_hours=data['basic_work_hours'],
				sick_leaves=data['sick_leaves'],
				casual_leaves=data['casual_leaves'],
			)
			return Response({
			"statuscode": status.HTTP_200_OK,
			"status": "success",
			"message": "company updated successfully"
		}, status=status.HTTP_200_OK)
	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
				
@api_view(('DELETE',))
def company_delete(request,pk):
	comp = check_company_exists(pk)
	if comp:
		company.objects.filter(company_id = pk).update(is_active = False)
		return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "message" : "company deleted successfully"}, status = status.HTTP_204_NO_CONTENT)