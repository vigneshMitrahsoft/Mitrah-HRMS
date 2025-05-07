from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from company.models import company

class EmployeeManager(BaseUserManager):
	def create_user(self, email, password=None, **extra_fields):
		if not email:
			raise ValueError('The Email field must be set')
		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user
	
	def create_superuser(self, email, password=None, **extra_fields):
		extra_fields.setdefault('is_active', True)

		return self.create_user(email, password, **extra_fields)

	def get_by_natural_key(self, email):
		return self.get(email=email)

class roles(models.Model):
	role_id = models.BigAutoField(primary_key=True)
	role_name = models.CharField(max_length=100)
	
	class Meta:
		db_table = 'roles'

class employee_type(models.Model):
	type_id = models.BigAutoField(primary_key=True)
	type_name = models.CharField(max_length=100)

	class Meta:
		db_table = 'employee_type'
	
class employee(AbstractBaseUser, PermissionsMixin):
	employee_id = models.BigAutoField(primary_key=True)
	company_id = models.ForeignKey(company, on_delete=models.DO_NOTHING, related_name = 'companyid')
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	email = models.EmailField(max_length=150,unique=True)
	password = models.CharField(max_length=100,default=None)
	date_of_birth = models.DateField()
	address = models.CharField(max_length=100)
	# role_id = models.ForeignKey(employee_role, on_delete=models.DO_NOTHING, related_name = 'employee_roleid')
	date_of_joining = models.DateField()
	type_id = models.ForeignKey(employee_type, on_delete=models.DO_NOTHING, related_name = 'employee_typeid')
	employee_last_date = models.DateTimeField(default=None,null=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	created_by = models.IntegerField(null=True)
	updated_by = models.IntegerField(null=True)

	USERNAME_FIELD = 'email'
	
	objects = EmployeeManager()

	def get_user_id(self):
		return self.employee_id
	
	def __str__(self):
		return self.email

	class Meta:
		db_table = 'employee'

class employee_roles(models.Model):
	employee = models.ForeignKey('employee', on_delete=models.CASCADE)
	role = models.ForeignKey('roles', on_delete=models.CASCADE)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	created_by = models.IntegerField(null=True)
	updated_by = models.IntegerField(null=True)

	class Meta:
		db_table = 'employee_roles'
		unique_together = ('employee', 'role')
		

class employee_salary_info(models.Model):
	salary_id = models.BigAutoField(primary_key=True)
	employee_id = models.OneToOneField(employee, on_delete=models.DO_NOTHING, related_name = 'employee_salary')
	gross_salary = models.FloatField(blank=True, null=True)
	variable_pay = models.FloatField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	created_by = models.IntegerField(null=True)
	updated_by = models.IntegerField(null=True)
	
	class Meta:
		db_table = 'employee_salary_info'

