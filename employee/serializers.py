from .models import company,employee,employee_type,employee_roles,roles,employee_salary_info
from rest_framework import  serializers

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
	# type_id = serializers.PrimaryKeyRelatedField(queryset=employee_type.objects.all(), required=True)
	type_id = serializers.SerializerMethodField()
	roles = serializers.SerializerMethodField()
	gender = serializers.IntegerField(required = True)
	phone = serializers.IntegerField(required = True)
	aadhar_number = serializers.IntegerField(required = False)
	pan_number = serializers.CharField(required = False)
	profile_picture_path = serializers.CharField(required = False)

	def get_roles(self, obj):
		roles = employee_roles.objects.filter(employee=obj, is_active=True).select_related("role")
		return [{"role_id": role.role.role_id, "role_name": role.role.role_name} for role in roles]
	
	def get_type_id(self,obj):
		type = employee_type.objects.filter(type_id = obj.type_id.type_id)
		return [{'type_id': type.type_id, 'type_name': type.type_name} for type in type]
	
	def to_representation(self, instance):
		request = self.context['request']
		data = super().to_representation(instance)
		gender_map = {
			0: "Female",	
			1: "Male",
		}
		gender_value = data.get("gender")
		data["gender"] = gender_map.get(gender_value, "Not defined")
		request_url = request.build_absolute_uri('/')[:-1]
		file_directory = '/assets/profile_picture/'
		if data['profile_picture_path'] != None:
			data['profile_picture_path'] = request_url + file_directory + data['profile_picture_path']

		return data
	
class create_serializer(serializers.Serializer):
	company_id = serializers.PrimaryKeyRelatedField(queryset=company.objects.all(), required=True)
	first_name = serializers.CharField(required = True)
	last_name = serializers.CharField(required = True)
	email = serializers.EmailField(required = True)
	password = serializers.CharField(required = True)
	date_of_birth = serializers.DateField(required = True)
	gender = serializers.IntegerField(required = True)
	phone = serializers.IntegerField(required = True)
	aadhar_number = serializers.IntegerField(required = False)
	pan_number = serializers.CharField(required = False)
	profile_picture_path = serializers.CharField(required = False)
	address = serializers.CharField(required = True)
	role_ids = serializers.ListField(child=serializers.PrimaryKeyRelatedField(queryset=roles.objects.all()), required=True)
	date_of_joining = serializers.DateField(required = True)
	type_id = serializers.PrimaryKeyRelatedField(queryset=employee_type.objects.all(), required=True)

	def validate(self,data):
		data['email']= data['email'].lower()
		user_exists = employee.objects.filter(email=data['email']).exists()
		if user_exists:
			raise serializers.ValidationError({"error":"Email already exists."})
		if len(str(data['phone'])) != 10:
			raise serializers.ValidationError({"error":"Phone number must contain 10 digits"})
		if data['gender'] not in [0,1]:
			raise serializers.ValidationError({"error":"Gender must be 0 or 1"})
		return data
	
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
			'company_id', 'first_name', 'last_name', 'email', 'password','gender','phone','aadhar_number','pan_number',
			'date_of_birth', 'address', 'role_ids', 'date_of_joining', 'type_id', 'updated_by','profile_picture_path'
		]

	def validate_role_ids(self, value):
		# Ensure there are no duplicates in the provided role IDs
		role_ids_set = {role for role in value}
		if len(role_ids_set) != len(value):
			raise serializers.ValidationError("Duplicate role IDs are not allowed.")
		return value

class create_salary_info_serializer(serializers.ModelSerializer):
	class Meta:
		model = employee_salary_info
		fields = "__all__"
