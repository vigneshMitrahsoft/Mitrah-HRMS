from .models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .serializers import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView


@api_view(('GET',))
def get_employee(request,id):
    try:
        data = employee.objects.get(employee_id = id,is_active=True)
    except employee.DoesNotExist:
        return Response({"detail": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
    serialized_data = get_serializer(data)
    return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)

@api_view(('GET',))
@permission_classes((IsAuthenticated,))
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
        create_employee = employee.objects.create(**data, created_by =1, updated_by =1)
        return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"created successfully"},status=status.HTTP_201_CREATED)
    else:
        print('errors', serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(('PATCH',))
def update_employee(request,id):
    try:
        employee_data = employee.objects.get(employee_id = id)
    except employee_data.DoesNotExist:
        return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
    serializer = employee_serializer(employee_data, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save() 
        return Response({"statuscode":status.HTTP_200_OK,"status":"success","message":"updated successfully"},status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(('DELETE',))
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




        
    
