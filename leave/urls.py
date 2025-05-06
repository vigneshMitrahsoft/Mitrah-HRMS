from django.urls import path
from . import api

urlpatterns = [
	path("",api.get_employees_leave_balances),
	path("<int:id>",api.get_employee_leave_balances),
	path("create", api.create_employee_leave_balances),
	path("apply",api.apply_employee_leaves),
	path("applied_leaves",api.get_employees_applied_leaves),
	path("applied_leaves/<int:id>",api.get_employee_applied_leaves),
	path("update/<int:id>",api.update_employee_applied_leaves)
]