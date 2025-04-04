from django.urls import path
from . import api

urlpatterns = [
    path('',api.shift_list,name='shift_get'),
    path('create', api.shift_create, name='shift_create'),
    path('<int:id>', api.shift_view, name='shift_view'),
    path('update/<int:id>', api.shift_update, name='shift_update'),
    path('delete/<int:id>', api.shift_delete, name='shift_delete'),
]