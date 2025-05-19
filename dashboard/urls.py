from django.urls import path
from . import api

urlpatterns = [
	path("hr", api.dashboard, name="hr_dashboard"),
	path("employee", api.employee_dashboard, name="employee_dashboard")
]