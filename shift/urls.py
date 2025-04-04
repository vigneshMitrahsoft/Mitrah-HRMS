from django.urls import path
from . import views

urlpatterns = [
    path('type',views.shift_type_list,name='shift_type_get'),
    path('type/create', views.shift_type_create, name='shift_type_create'),
    path('type/<int:ID>', views.shift_type_view, name='shift_type_view'),
    path('',views.shift_list,name='shift_get'),
    path('create', views.shift_create, name='shift_create'),
    path('<int:ID>', views.shift_view, name='shift_view'),
    
    path('employeelist',views.emp_shift_list,name='shift_get'),
]