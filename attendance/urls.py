from django.urls import path
from . import views
from . import api
urlpatterns = [
    path("attendance",api.attendance_entry)
]