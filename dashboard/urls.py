from django.urls import path
from . import api

urlpatterns = [
	path("hr", api.dashboard, name="hr_dashboard"),
	path("employee", api.employeedashboard, name="employee_dashboard")
]