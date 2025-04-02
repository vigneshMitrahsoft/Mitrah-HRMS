from django.urls import path
from . import views
from . import api
urlpatterns = [
    path("<int:id>",api.get_employee_attendance_details),
    path("checkin",api.check_in_entry),
    path("checkout",api.check_out_entry)
]