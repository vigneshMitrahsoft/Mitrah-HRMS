from django.urls import path
from . import api

urlpatterns = [
	path("",api.get_employees_leave_balances),
	path("<int:id>",api.get_employee_leave_balances),
	# path("create", api.create_employee_leave_balances),
	path("update/<int:id>",api.update_employee_leave_balance),
	path("apply",api.apply_employee_leaves),
	path("applied_leaves",api.get_employees_applied_leaves),
	path("applied_leaves/<int:id>",api.get_employee_applied_leaves),
	path("update/<int:id>",api.update_employee_applied_leaves),
	path("permission/apply",api.apply_employee_permission),
	path("permission/update/<int:id>",api.update_employee_permission),
	path("permission",api.get_employees_applied_permissions),
	path("permission/<int:id>",api.get_employee_applied_permissions)
]