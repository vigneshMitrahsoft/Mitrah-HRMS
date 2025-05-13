from datetime import datetime,timedelta
from django.shortcuts import render
from rest_framework.decorators import api_view
from .models import company, company_Settings
from .serializers import companySerializer, companyCreateSerializer, companyUpdateSerializer
from rest_framework.response import Response
from rest_framework import status

def company_exists(pk):
	try:
		comp = company.objects.filter(company_id = pk)
	except company.DoesNotExist:
		return Response ({"details" : "company not found"}, status = status.HTTP_404_NOT_FOUND)
	return comp

@api_view(('GET',))
def company_list(request):
	companies = company.objects.filter(is_active = True)
	serializer = companySerializer(companies, many = True)
	return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "data" : serializer.data}, status = status.HTTP_200_OK)

@api_view(('GET',))
def specific_company(request, pk):
	comp = company.objects.get(company_id = pk)
	serializer = companySerializer(comp)
	return Response ({"statuscode" : status.HTTP_200_OK, "status" : "success", "data" : serializer.data}, status = status.HTTP_200_OK)

@api_view(('POST',))
def company_create(request):
	data = request.data
	hours = data['permission_hours']
	seconds = int(hours * 3600)
	time_conversion = str(timedelta(seconds=seconds))
	data['permission_hours'] = time_conversion
	serializer = companyCreateSerializer(data = request.data)
	if serializer.is_valid():
		datas = serializer.validated_data
		comp = company.objects.create(company_name = datas['company_name'], address = datas['address'], created_at = datetime.now())
		company_Settings.objects.create(
			HRA = datas['hra'],
			employer_ESI = datas['employer_ESI'],
			employee_ESI = datas['employee_ESI'], 
			employer_PF = datas['employer_PF'],
			employee_PF = datas['employee_PF'],
			leave_compensation = datas['leave_compensation'],
			basic_work_hours = datas['basic_work_hours'],
			sick_leaves = datas['sick_leaves'],
			casual_leaves = datas['casual_leaves'],
			basic_pay = datas['basic_pay'],
			other_allowances = datas['other_allowances'],
			permission_hours = datas['permission_hours'],
			company_id = comp.company_id)
		return Response({"statuscode" : status.HTTP_201_CREATED, "status" : "success", "message" : "company created successfully"}, status = status.HTTP_201_CREATED)
	return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

@api_view(('PATCH',))
def company_update(request,pk):
	comp = company_exists(pk)
	serializer = companyUpdateSerializer(comp, data = request.data, partial = True)
	if serializer.is_valid():
		datas = serializer.validated_data
		comp = company.objects.filter(company_id = pk).update(company_name = datas['company_name'] ,address = datas['address'], updated_at = datetime.now())
		company_Settings.objects.filter(company_id = pk).update(
			hra = datas['hra'],
			employer_ESI = datas['employer_ESI'],
			employee_ESI = datas['employee_ESI'],
			employer_PF = datas['employer_PF'],
			employee_PF = datas['employee_PF'],
			leave_compensation = datas['leave_compensation'],
			basic_work_hours = datas['basic_work_hours'],
			sick_leaves = datas['sick_leaves'],
			casual_leaves = datas['casual_leaves'],
		)
		return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "message" : "company updated successfully"}, status = status.HTTP_200_OK)   
	return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
		 
		

@api_view(('DELETE',))
def company_delete(request,pk):
	comp = company_exists(pk)
	if comp:
		company.objects.filter(company_id = pk).update(is_active = False)
		return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "message" : "company deleted successfully"}, status = status.HTTP_204_NO_CONTENT)