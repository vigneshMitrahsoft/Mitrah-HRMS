from .models import company,employee, employee_role,employee_type
from rest_framework import  serializers
# from django.contrib.auth.hashers import make_password
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer,TokenRefreshSerializer
# from rest_framework.exceptions import AuthenticationFailed
# from rest_framework import status

class company_serializer(serializers.ModelSerializer):
    class Meta:
        model = company 
        fields = "__all__"

class employee_serializer(serializers.ModelSerializer):
    class Meta:
        model = employee
        fields = "__all__"


class get_serializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    company_id = serializers.PrimaryKeyRelatedField(queryset=company.objects.all(), required=True)
    first_name = serializers.CharField(required = True)
    last_name = serializers.CharField(required = True)
    email = serializers.EmailField(required = True)
    date_of_birth = serializers.DateField(required = True)
    address = serializers.CharField(required = True)
    # role_ids = serializers.ListField(child=serializers.PrimaryKeyRelatedField(queryset=roles.objects.all()), required=True)
    date_of_joining = serializers.DateField(required = True)
    type_id = serializers.PrimaryKeyRelatedField(queryset=employee_type.objects.all(), required=True)
    roles = serializers.SerializerMethodField()

    def get_roles(self, obj):
        roles = employee_roles.objects.filter(employee=obj, is_active=True).select_related("role")
        return [{"role_id": role.role.role_id, "role_name": role.role.role_name} for role in roles]
class create_serializer(serializers.Serializer):
    company_id = serializers.PrimaryKeyRelatedField(queryset=company.objects.all(), required=True)
    first_name = serializers.CharField(required = True)
    last_name = serializers.CharField(required = True)
    email = serializers.EmailField(required = True)
    password = serializers.CharField(required = True)
    date_of_birth = serializers.DateField(required = True)
    address = serializers.CharField(required = True)
    role_ids = serializers.ListField(child=serializers.PrimaryKeyRelatedField(queryset=roles.objects.all()), required=True)
    date_of_joining = serializers.DateField(required = True)
    type_id = serializers.PrimaryKeyRelatedField(queryset=employee_type.objects.all(), required=True)

    def validate(self,data):
        data['email']= data['email'].lower()
        user_exists = employee.objects.filter(email=data['email']).exists()
        if user_exists:
            raise serializers.ValidationError({"error":"Email already exists."})
        return data
    
    # def get_company_id(self, data):
    #     return company.objects.get(company_id = data.company_id)

    # def get_password(self, data):
    #     return make_password(data['password'])


class update_serializer(serializers.ModelSerializer):
    # This will directly accept a list of role IDs (primary keys)
    role_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=roles.objects.all()),
        required=False,
        allow_empty=True
    )

    class Meta:
        model = employee
        fields = [
            'company_id', 'first_name', 'last_name', 'email', 'password',
            'date_of_birth', 'address', 'role_ids', 'date_of_joining', 'type_id'
        ]

    def validate_role_ids(self, value):
        # Ensure there are no duplicates in the provided role IDs
        role_ids_set = {role for role in value}
        if len(role_ids_set) != len(value):
            raise serializers.ValidationError("Duplicate role IDs are not allowed.")
        return value


# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)

#         token['first_name'] = user.first_name
#         token['last_name'] = user.last_name
#         return token
    
#     def validate(self, attrs):
#         try:
#             data = super().validate(attrs)
#             response = {
#                 'status_code': status.HTTP_200_OK,
#                 'status' : 'success',
#                 'refresh_token' : data.pop('refresh'),
#                 'access_token' : data.pop('access')
#             }

#             return response
#         except AuthenticationFailed:
#             raise AuthenticationFailed({
#                 'status': 'error',
#                 'status_code': status.HTTP_401_UNAUTHORIZED,
#                 'message': 'Unauthorized User. Invalid username or password. Please try again'
#             })
        
# class customTokenRefreshSerializer(TokenRefreshSerializer):
#     def validate(self, attrs):
#         print("attrs", attrs)
#         data = super().validate(attrs)  # Get the default validated data

#         # Add custom response fields
#         return {
#             'status_code': status.HTTP_200_OK,
#             'status': 'success',
#             'access_token': data['access'],
#             'refresh_token': data.get('refresh'),  # Ensure refresh token is returned
#             'message': 'Token refreshed successfully'
#         }