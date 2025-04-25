from .models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .serializers import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
# from auth.permissions import HasRequiredRolesWithRoles #,CustomTokenAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.state import token_backend

def role_required(required_roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            auth_header = request.headers.get("Authorization", None)
            if not auth_header:
                return Response({"detail": "Authorization token missing"}, status=status.HTTP_401_UNAUTHORIZED)

            try:
                token = auth_header.split(" ")[1] 
                print(token, "token")
                decoded_token = token_backend.decode(token)
                print(decoded_token, "decoded_token")
                employee_id = decoded_token.get("employee_id")
                print(employee_id, "employee_id")

                if not employee_id:
                    return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

                
                employee_rolez = list(employee_roles.objects.filter(
                    employee_id=employee_id, is_active=True
                ).values_list("role__role_name", flat=True))

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
@role_required(['hr'])
def get_employee(request,id):
    try:
        data = employee.objects.get(employee_id = id,is_active=True)
    except employee.DoesNotExist:
        return Response({"detail": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
    serialized_data = get_serializer(data)
    return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)

@api_view(('GET',))
@permission_classes([IsAuthenticated])
@role_required(['hr']) 
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
        print(role_ids,"role_ids")
        create_employee = employee.objects.create(**data, created_by =1, updated_by =1)
        for role in role_ids:
            employee_roles.objects.create(employee_id = create_employee.employee_id, role_id = role.role_id)
        return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"created successfully"},status=status.HTTP_201_CREATED)
    else:
        print('errors', serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(('PATCH',))
@permission_classes((IsAuthenticated,))
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
@permission_classes((IsAuthenticated,))
@role_required(['hr'])
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




        
    
