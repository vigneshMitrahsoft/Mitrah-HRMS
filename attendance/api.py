from .models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status
# from .serializers import *
from datetime import date,datetime

@api_view(('POST',))
def attendance_entry(request):
    employee_id =5
    entry = 1
    today = date.today()
    current_date_time = datetime.now()
    print("today--->",today)
    if entry == 1:
        try:
            today_attendance_check = employee_attendance.objects.get(employee_id = employee_id, date = today)
        except employee_attendance.DoesNotExist:
            data ={
                "employee_id":employee_id,
                "date":today, 
            }
            attendance_entry = employee_attendance
            

    return Response({"statuscode":status.HTTP_201_CREATED,"status":"success"},status=status.HTTP_201_CREATED)

