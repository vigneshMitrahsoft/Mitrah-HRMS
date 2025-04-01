from django.urls import path
from . import views

urlpatterns = [
    path("", views.company_list, name="company_list"),
    path('create',views.company_create,name='company_create'),
    path('update/<int:pk>',views.company_update, name="company_update"),
    path('delete/<int:pk>',views.company_delete,name='company_delete')
]