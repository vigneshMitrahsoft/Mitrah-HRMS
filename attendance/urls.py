from django.urls import path
from . import views
from . import api
urlpatterns = [
    path("<int:id>",api.get_employee_attendance),
    path("checkin",api.check_in_entry),
    path("checkout",api.check_out_entry),
    path("attendanceinfo/create",api.create_employee_attendance_info),
    path("attendanceinfo/update",api.update_employee_attendance_info),
    path("update/<int:id>",api.update_employee_attendance_entries),
    path("attendanceinfo/<int:id>",api.get_employee_attendance_report),
    path("attendanceinfo",api.get_all_employee_attendance_report)
]