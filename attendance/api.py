from .models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import *
from datetime import date,datetime,time, timedelta
from django.utils import timezone
from django.db import connection

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
        if today_entry.check_in is  None:
            print("hloooo--->")
            today_entry.check_in = current_date_time
            today_entry.save()
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
            return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"checkin successfully"},status=status.HTTP_201_CREATED)
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
                attendance_info_data['status'] = "Present"
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
                today_entry.effective_hours = effective_hours
                today_entry.save()
    except employee_attendance.DoesNotExist:
        return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","message":"No attendance record found for today. Please check in first."},status=status.HTTP_400_BAD_REQUEST)
    #TODO: have to get conirmation for the last checkout entry for the employee continuously work for next day
    return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"checkout successfully"},status=status.HTTP_201_CREATED)

@api_view(('POST',))
def get_employee_attendance(request,id):
    # NOTE:Before call the api you need to run the get_employee_attendance sql file in db_schema into the postgres db then call the api
    #TODO: have to get the employee holidays and display into it
    data = request.data
    query = "SELECT * FROM fn_get_employee_attendance(%s, %s, %s)"
    with connection.cursor() as cursor:
        cursor.execute(query,[id,data['month'],data['year']])
        result = cursor.fetchall()
    column_names = [
    'date', 'day','is_week_off','attendance_status', 'leave_status',
    'check_in', 'check_out', 'effective_hours', 'total_hours'
    ]
    result_dict = [
            dict(zip(column_names, row)) for row in result
    ]
    for result in result_dict:
        result["check_in"] = result["check_in"].strftime("%Y-%m-%d:%H:%M:%S") if result["check_in"] else "00:00:00"
        result["check_out"] = result["check_out"].strftime("%Y-%m-%d:%H:%M:%S") if result["check_out"] else "00:00:00" 
    serializer = get_employee_attendance_serializer(result_dict,many = True)

    return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serializer.data},status=status.HTTP_200_OK)
@api_view(('POST',))
def create_employee_attendance_info(request):
    serializer = create_attendance_byinfo_serializer(data = request.data)
    if serializer.is_valid():
        try:
            attendance_info = employee_attendance.objects.get(employee_id = request.data['employee_id'],date = request.data['date'])
        except employee_attendance.DoesNotExist:
            attendance = employee_attendance.objects.create(**serializer.validated_data)
            attendance_id = attendance.attendance_id
            request.data['attendance_id'] = attendance_id
            serializer = atttendance_info_post_serializer(data = request.data)
            if serializer.is_valid():
                data = serializer.validated_data
                create_attendance_info = employees_attendance_info.objects.create(**data, action_by =1)
                return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"created successfully"},status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","detail": "Employee_attendance already exist."}, status=status.HTTP_404_NOT_FOUND)

@api_view(('PATCH',))
def update_employee_attendance_info(request):
    id = request.data['employee_id']
    attendance_id = request.data['attendance_id']
    try:
        employee_data = employees_attendance_info.objects.get(employee_id = id, attendance_id = attendance_id)
    except employee_data.DoesNotExist:
        return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","detail": "Employee_attendance_info not found."}, status=status.HTTP_404_NOT_FOUND)
    serializer = attendance_info_serializer(employee_data, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save() 
        return Response({"statuscode":status.HTTP_200_OK,"status":"success","message":"updated successfully"},status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(('PATCH',))
# def update_employee_attendance_entries(request,id):
#     data = request.data
#     if 'check_in' not in data and 'check_out' not in data:
#         return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","detail": "Please provide checkin or checkout time"}, status=status.HTTP_404_NOT_FOUND) 
#     if 'check_in' in data:
#         today_entry = attendance_entries.objects.get(entry_id = id)
#         check_in_date = today_entry.checkin_entry
#         print("totay_entry---->",check_in_date)
#         check_in_date = check_in_date.replace(hour = 10, minute = 30, second = 0)
#         print("modify---->",check_in_date)
#     if 'check_out' in data:
#         print("check_out entry")
#     employee_id = attendance_entries.objects.filter(attendance_id = today_entry.attendance_id)
#     for emp in employee_id:
#         print("employeee--->",emp.checkin_entry)

@api_view(('PATCH',))
def update_employee_attendance_entries(request,id):
    data = request.data
    if 'check_in' not in data and 'check_out' not in data:
        return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","detail": "Please provide checkin or checkout time"}, status=status.HTTP_404_NOT_FOUND) 
    today_entry = attendance_entries.objects.get(entry_id = id)
    if 'check_in' in data:
        check_in_date = today_entry.checkin_entry
        print("totay_entry---->",check_in_date)
        update_checkin_date = data['check_in'].strip().replace(".", ":").split(":")
        # update_checkin_date = update_checkin_date.replace(".", ":")
        # update_checkin_date = update_checkin_date.split(":")
        print("update_checkin_date----->",update_checkin_date[0],update_checkin_date[1])
        hour = int(update_checkin_date[0])
        minute = int(update_checkin_date[1])
        try:
            second = int(update_checkin_date[2])
        except:
            second = 0
        check_in_date = check_in_date.replace(hour = hour, minute = minute , second = second)
        print("modify---->",check_in_date)
        # today_entry.checkin_entry = check_in_date       #TODO must be uncommented to update the checkin entry
        # today_entry.save()
    if 'check_out' in data:
        print("check_out entry")
        check_out_date = today_entry.checkout_entry
        print("totay_entry---->",check_out_date)
        update_checkout_date = data['check_out'].strip().replace(".", ":").split(":")
        # update_checkout_date = update_checkout_date.replace(".", ":")
        # update_checkout_date = update_checkout_date.split(":")
        print("update_checkout_date----->",update_checkout_date[0],update_checkout_date[1])
        hour = int(update_checkout_date[0])
        minute = int(update_checkout_date[1])
        try:
            second = int(update_checkout_date[2])
        except:
            second = 0
        check_out_date = check_out_date.replace(hour = hour, minute = minute , second = second)
        print("modify---->",check_out_date)
        # today_entry.checkout_entry = check_out_date      #TODO must be uncommented to update the checkout entry
        # today_entry.save()

    employee_id = attendance_entries.objects.filter(attendance_id = today_entry.attendance_id).order_by('entry_id')
    
    for emp in employee_id:
        time_difference = emp.checkout_entry - emp.checkin_entry
        effective_hours_entries = convert_timedelta_to_time(time_difference)
        print("emp->",emp)
        print("emp2->",employee_id.last())
        
        if emp == employee_id[0]:
            total_entry = effective_hours_entries 
            print("entries1 ---->",emp.checkin_entry,emp.checkout_entry)
            # print("emp length---->",len(emp))
            # print("emp length---->",len(employee_id))

        if emp.entry_id == employee_id.last().entry_id:
            print("hiiii last entry")
            
        else:
            print("entries ---->",emp.checkin_entry,emp.checkout_entry)
            print("the result ---->",total_entry,effective_hours_entries)
            total_entry = add_effective_time(total_entry,effective_hours_entries)
            print("total_entry----->",total_entry)
        
        
    print("employeee--->",total_entry)
    attendance_id = today_entry.attendance_id
    employee_attendace = employee_attendance.objects.get(attendance_id = attendance_id.attendance_id)
    print("employee_attendance----->",employee_attendace.total_hours)
    total_hours = employee_attendace.check_out - employee_attendace.check_in
    print("total_hours----->",total_hours)
    today_entry = convert_timedelta_to_time(total_hours)
    print("today_entry----->",today_entry)
    




