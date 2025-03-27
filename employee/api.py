from .models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import *
from django.contrib.auth.hashers import make_password
# 

@api_view(('GET',))
def get_employee(request,id):
    try:
        data = employee.objects.get(employee_id = id,is_active=True)
    except employee.DoesNotExist:
        return Response({"detail": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
    serialized_data = get_serializer(data)
    return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)

@api_view(('GET',))
def get_employees(request):
    print("fhkgh")
    data = employee.objects.filter(is_active=True)
    serialized_data = get_serializer(data,many = True)
    return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)

@api_view(('POST',))
def create_employee(request):
    # company.objects.create(
    #     company_name = 'Mitrahsoft',
    #     address = 'Mitrahsoft, Madurai'
    # )
    serializer = create_serializer(data = request.data)
    if serializer.is_valid():
        data = serializer.data
        companyObj = company.objects.get(company_id = data['company_id'])
        encrypted_password = make_password(data['password'])
        print("encrypted_password--->", encrypted_password)
        data.pop('company_id')
        data.pop('password')
        create_employee = employee.objects.create(**data, password = encrypted_password, company_id = companyObj, created_by =1, updated_by =1)
        return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"created successfully","data":serializer.data},status=status.HTTP_201_CREATED)
    else:
        print('errors', serializer.errors)

@api_view(('PATCH',))
def update_employee(request,id):
    try:
        employee_data = employee.objects.get(employee_id = id)
    except employee_data.DoesNotExist:
        return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
    serializer = get_serializer(employee_data, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"statuscode":status.HTTP_200_OK,"status":"success","message":"updated successfully","data":serializer.data},status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(('DELETE',))
def delete_employee(request, id):
    employee_delete = employee.objects.get(employee_id=id)
    employee_delete.is_active = True
    employee_delete.save()
    return Response({"statuscode": status.HTTP_200_OK, "status": "success", "message": " Deleted successfully."}, status=status.HTTP_200_OK)






        
    
