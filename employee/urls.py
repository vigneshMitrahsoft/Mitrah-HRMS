from django.urls import path
from . import views
from . import api
from rest_framework_simplejwt.views import (
	TokenObtainPairView,
	TokenRefreshView,
)

urlpatterns = [
	path("", api.get_employees),
	path("create", api.create_employee),
	path("<int:id>", api.get_employee),
	path("update/<int:id>", api.update_employee),
	path("delete/<int:id>", api.delete_employee),
	# path("login", api.login),
	path("salary/create",api.create_employee_salary_info),
	path("salary/update/<int:id>",api.update_employee_salary_info),
	path("salary",api.get_employees_salary),
	path("salary/<int:id>",api.get_employee_salary),
	path("roles",api.get_employee_roles)
	# path("salary/calculate/<int:id>",api.calculate_employee_salary)
	# path("employees",views.get),
	# path("employee",views.insertEmployee),
	# path('addemployee',views.addEmployee),
	# path("employee/<int:id>",views.employeeUpdate),
	# path("password",views.passsword_check),
	# path("delete/<int:id>",views.delete),
	# path("token", TokenObtainPairView.as_view(), name="token_obtain_pair"),  
	# path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
]