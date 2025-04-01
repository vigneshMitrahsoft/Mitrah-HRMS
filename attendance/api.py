from .models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import *
from datetime import date,datetime
from django.utils import timezone
import tzlocal

@api_view(('POST',))
def check_in_entry(request):
    employee_id = 9
    today = date.today()
    current_date_time = datetime.now()
    try:
        today_entry = employee_attendance.objects.get(employee_id = employee_id, date = today)
        if today_entry.check_out is not None:
            data = {
                "attendance_id":today_entry.attendance_id,
                "checkin_entry":current_date_time
            }
            serializer = attendance_entry_serializer(data = data)
            if serializer.is_valid():
                attendance_entries.objects.create(**serializer.validated_data)
            # remove the checkout value when user will checkin
            today_entry.check_out = None
            today_entry.save()
        else:
            return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","message":"You already checkin please checkout"},status=status.HTTP_400_BAD_REQUEST)
    except employee_attendance.DoesNotExist:
        data ={
            "employee_id":employee_id,
            "date":today,
            "check_in":current_date_time,
        }
        attendance_entry = create_attendance_serializer(data = data)
        if attendance_entry.is_valid():
            data = attendance_entry.validated_data
            employee_checkin = employee_attendance.objects.create(**data,created_by = 1,updated_by = 1)

            entries_data = {
                "attendance_id":employee_checkin.attendance_id,
                "checkin_entry":current_date_time
            }
            serializer = attendance_entry_serializer(data = entries_data)
            if serializer.is_valid():
                attendance_entries.objects.create(**serializer.validated_data)
            attendance_info_data = {
                "employee_id":employee_id,
                "date":today,
                "attendance_id":employee_checkin.attendance_id
            }
            try:
                print("try block--->")
                check_applied_leave = employee_applied_leaves.objects.get(employee_id = employee_id, start_date = today)
                leave_type = check_applied_leave.leave_type
                if leave_type == "remote":
                    attendance_info_data['status'] = check_applied_leave.session + "_" + leave_type
                else:
                    attendance_info_data['status'] = leave_type
            except employee_applied_leaves.DoesNotExist:
                print("except block--->")
                attendance_info_data['status'] = "Present"
                print("except block--->",attendance_info_data)
            serializer = attendance_info_serializer(data = attendance_info_data)
            if serializer.is_valid():
                employees_attendance_info.objects.create(**serializer.validated_data)
    return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"checkin successfully"},status=status.HTTP_201_CREATED)

@api_view(('POST',))
def check_out_entry(request):
    employee_id = 9
    today = date.today()
    current_date_time = datetime.now()
    local_timezone = tzlocal.get_localzone()
    current_time = datetime.now(local_timezone)
    try:
        today_entry = employee_attendance.objects.get(employee_id = employee_id, date = today)
        if today_entry.check_out is not None:
            return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","message":"You already checkout please checkin"},status=status.HTTP_400_BAD_REQUEST)
        else:
            today_entry.check_out = current_date_time
            today_entry.save()
            time_diff = today_entry.check_in - timezone.now()
            print("total time--->",time_diff)
            print("checkin time--->",today_entry.check_in)
            attendance_entry = attendance_entries.objects.filter(attendance_id = today_entry.attendance_id).last()
            attendance_entry.checkout_entry = current_date_time
            attendance_entry.save()
            time_difference = attendance_entry.checkin_entry- current_time
            print("efficient_time2--->",attendance_entry.checkin_entry)
            print("efficient_time2--->",current_time)
            print("efficient_time--->",time_difference)
    except employee_attendance.DoesNotExist:
        return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","message":"No attendance record found for today. Please check in first."},status=status.HTTP_400_BAD_REQUEST)
    
    return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"checkout successfully"},status=status.HTTP_201_CREATED)

