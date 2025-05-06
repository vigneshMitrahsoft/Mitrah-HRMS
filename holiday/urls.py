from django.urls import path,include
from . import views
from . import api

urlpatterns = [
    path('',api.index,name = 'holiday_list'),
    path('create/',api.create_holiday,name = 'holiday_create'),
    path('delete/<int:id>/',api.delete_holiday,name = 'holiday_delete'),
    path('update/<int:id>/',api.update_holiday,name = 'holiday_update'),
]