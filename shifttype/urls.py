from django.urls import path
from . import api

urlpatterns = [
    path('', api.shift_type_list, name = 'shift_type_get'),
    path('create', api.shift_type_create, name = 'shift_type_create'),
    path('<int:id>', api.shift_type_view, name = 'shift_type_view'),
    path('update/<int:id>', api.shift_type_update, name = 'shift_type_update'),
    path('delete/<int:id>', api.shift_type_delete, name = 'shift_type__delete'),
]