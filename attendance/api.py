from .models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import *
from datetime import date,datetime,time, timedelta
from django.utils import timezone
# import pytz

def convert_timedelta_to_time(time_diff):
    hours = time_diff.seconds // 3600
    minutes = (time_diff.seconds // 60) % 60
    seconds = time_diff.seconds % 60
    converted_time = time(hour=hours, minute=minutes, second=seconds)
    return converted_time

def add_effective_time(old_effective_time, new_effective_time):
    def time_to_timedelta(t):
        return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)


    first_time_delta = time_to_timedelta(old_effective_time)
    second_time_delta = time_to_timedelta(new_effective_time)

    total_time_delta = first_time_delta + second_time_delta

    total_seconds = total_time_delta.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    result_time = datetime(1900, 1, 1, int(hours), int(minutes), int(seconds)).time()
    return result_time
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
                #TODO: need to get the date filter after insert the values in the applied leaves
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
    #TODO: have to get the employee_id from json response
    employee_id = 9
    today = date.today()
    current_date_time = datetime.now()
    try:
        today_entry = employee_attendance.objects.get(employee_id = employee_id, date = today)
        if today_entry.check_out is not None:
            return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","message":"You already checkout please checkin"},status=status.HTTP_400_BAD_REQUEST)
        else:
            today_entry.check_out = current_date_time  
            # today_entry.save()
            check_in_hours = today_entry.check_in.replace(tzinfo=None)
            total_time = current_date_time - check_in_hours
            today_entry.total_hours = convert_timedelta_to_time(total_time)
            today_entry.save()
            #TODO: have to change the date format into float the total hours contains float 
            # time_diff = today_entry.check_in - timezone.now()
            attendance_entry = attendance_entries.objects.filter(attendance_id = today_entry.attendance_id).last()
            attendance_entry.checkout_entry = current_date_time
            attendance_entry.save()
            attendance_value = attendance_entry.checkin_entry.replace(tzinfo=None)
            time_difference = current_date_time - attendance_value
            if today_entry.effective_hours is None:
                today_entry.effective_hours = convert_timedelta_to_time(time_difference)
                today_entry.save()
            else:
                total_hours_time = convert_timedelta_to_time(time_difference)
                effective_hours = add_effective_time(today_entry.effective_hours,total_hours_time)
                print("effective----->",effective_hours)
                today_entry.effective_hours = effective_hours
                today_entry.save()
    except employee_attendance.DoesNotExist:
        return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","message":"No attendance record found for today. Please check in first."},status=status.HTTP_400_BAD_REQUEST)
    #TODO: have to get conirmation for the last checkout entry for the employee continuously work for next day
    return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"checkout successfully"},status=status.HTTP_201_CREATED)

@api_view(('GET',))
def get_employee_attendance_details(request,id):
    employee_attendance_data = employee_attendance.objects.get(employee_id = id)
    serailizer = attendance_serializer(data = employee_attendance_data)
    # if serializer.is_valid():

@api_view(('POST',))
def get_employee_attendance_info(request):
    serializer = atttendance_info_post_serializer(data = request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        create_attendance_info = employees_attendance_info.objects.create(**data, action_by =1)
        return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"created successfully"},status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

