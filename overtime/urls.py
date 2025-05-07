from django.urls import path,include
from . import api

urlpatterns = [
	path("", api.overtime_list, name="overtime_list"),
	path("<int:pk>", api.overtime_detail, name="overtime_detail"),
	path("create", api.overtime_create, name="overtime_create"),
	path("update/<int:pk>", api.overtime_update, name="overtime_update"),
	path("delete/<int:pk>", api.overtime_delete, name="overtime_delete"),
	path("acceptance/<int:pk>", api.overtime_acceptance, name="overtime_acceptance"),
]

