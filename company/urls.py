from django.urls import path
from . import views
from . import api

urlpatterns = [
    path("", api.company_list, name="company_list"),
    path("<int:pk>",api.specific_company, name='specific_company'),
    path('create',api.company_create,name='company_create'),
    path('update/<int:pk>',api.company_update, name="company_update"),
    path('delete/<int:pk>',api.company_delete,name='company_delete')
]