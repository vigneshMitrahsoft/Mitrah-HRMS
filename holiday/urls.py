from django.urls import path
from . import api

urlpatterns = [
    path('import/', api.import_holidays,name = 'holiday_list'),
    path('create/', api.create_holiday, name = 'holiday_create'),
    path('delete/<int:id>/', api.delete_holiday, name = 'holiday_delete'),
    path('update/<int:id>/', api.update_holiday, name = 'holiday_update')
]