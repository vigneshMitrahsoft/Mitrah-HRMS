from .models import employee_leave_balances,employee_applied_leave_days, employee_applied_leaves, employee_applied_permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import create_leavebalance_serializer, get_leavebalance_serializer, create_employee_applied_leaves, create_employee_applied_leaves_days, get_employee_apllied_leaves,get_employee_applied_leave,create_applied_permission
from django.db.models import Prefetch
from datetime import datetime, timedelta
from attendance.api import convert_timedelta_to_time, add_effective_time
from attendance.models import employee_attendance, employees_attendance_info
from attendance.serializers import atttendance_info_post_serializer, create_attendance_byinfo_serializer

def calculate_permission_time(old_effective_time, new_effective_time):
    def time_to_timedelta(t):
        return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    first_time_delta = time_to_timedelta(old_effective_time)
    second_time_delta = time_to_timedelta(new_effective_time)
    total_time_delta = first_time_delta - second_time_delta
    total_seconds = total_time_delta.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    result_time = datetime(1900, 1, 1, int(hours), int(minutes), int(seconds)).time()
    return result_time

def time_duration(start_date, end_date):
	start_dt = datetime.strptime(str(start_date), "%H:%M")
	end_dt = datetime.strptime(str(end_date), "%H:%M")
	duration = end_dt - start_dt
	time = convert_timedelta_to_time(duration)
	return time

def check_employee_leave_availability(employee_leave_info):
	Total_days = 0
	sick_leave = 0
	casual_leave = 0
	for session in employee_leave_info['sessions']:
		if session['session'] == "Morning" or session['session'] == "Evening":
			Total_days += 0.5
		elif session['session'] == "Full Day":
			Total_days += 1
	employee_leave_balance = employee_leave_balances.objects.get(employee_id = employee_leave_info['employee_id'])
	if employee_leave_info['leave_type'] == "Sick Leave":
		leave_balance = employee_leave_balance.sick_leave
	elif employee_leave_info['leave_type'] == "Casual Leave":
		leave_balance = employee_leave_balance.casual_leave
	
	return Total_days, leave_balance

def check_existing_permission(data):
	check = employee_applied_permissions.objects.filter(employee = data['employee'], permission_date = data['permission_date'])
	start_time = datetime.strptime(data['start_time'], "%H:%M").time()
	if check:
		for check_value in check:
			if check_value.start_time <= start_time <= check_value.end_time:
				return True
	else:
		return False
	return False

@api_view(('POST',))
def create_employee_leave_balances(request):
	data  = {
		'employee_id': 10,
		'sick_leave': 5,
		'casual_leave': 1,
		'permissions': 1,
		'compensation_leave': 1
	}
	serializer = create_leavebalance_serializer(data=data)
	if serializer.is_valid():
		data = serializer.validated_data
		create_leave_balance = employee_leave_balances.objects.create(**data , created_by = 1, updated_by = 1)
		return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"created successfully"},status=status.HTTP_201_CREATED)
	else:
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
@api_view(('GET',))
def get_employees_leave_balances(request):
	try:
		data = employee_leave_balances.objects.all()
	except employee_leave_balances.DoesNotExist:
		return Response({"detail": "Employee leave balance not found"}, status=status.HTTP_404_NOT_FOUND)
	serialized_data = get_leavebalance_serializer(data, many = True)
	
	return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)

@api_view(('GET',))
def get_employee_leave_balances(request,id):
	try:
		data = employee_leave_balances.objects.get(leave_balance_id = id)
	except employee_leave_balances.DoesNotExist:
		return Response({"detail": "Employee leave balance not found"}, status=status.HTTP_404_NOT_FOUND)
	serialized_data = get_leavebalance_serializer(data)
   
	return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)

@api_view(('POST',)) 
def apply_employee_leaves(request):
	employee_leave_info = request.data
	Total_days, leave_balance = check_employee_leave_availability(employee_leave_info)
	employee_leave_balance = employee_leave_balances.objects.get(employee_id = employee_leave_info['employee_id'])
	if Total_days > leave_balance: 
		return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"failed","message":"Leave balance is not sufficient"})
	else:
		data = {
			'employee_id' : employee_leave_info['employee_id'],
			'start_date' : employee_leave_info['start_date'],
			'end_date' : employee_leave_info['end_date'],
			'leave_type' : employee_leave_info['leave_type'],
			'reason' : employee_leave_info['reason'],
			'status' : "Pending",
			'sessions' : employee_leave_info['sessions']
		}
		serializer = create_employee_applied_leaves(data = data)
		if serializer.is_valid():
			data = serializer.validated_data
			applied_leave = employee_applied_leaves.objects.create(
				employee_id = data['employee_id'],
				start_date = data['start_date'],
				end_date = data['end_date'],
				leave_type = data['leave_type'],
				reason = data['reason'],
				status = data['status'],
				action_by = 1
			)
			employee_applied_leave_days.objects.bulk_create([
				employee_applied_leave_days(
					applied_leave_request_id=applied_leave,
					leave_date=session_data['leave_date'],
					session=session_data['session'],
					comment=session_data['comment'],
					status=session_data['status']
				) for  session_data in data['sessions']
			])
			if employee_leave_info['leave_type'] == 'Sick Leave':
				employee_leave_balance.sick_leave = employee_leave_balance.sick_leave - Total_days
			else:
				employee_leave_balance.casual_leave = employee_leave_balance.casual_leave - Total_days
			employee_leave_balance.save()
			return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"Leave applied successfully"},status=status.HTTP_201_CREATED)

		else:
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(('GET',))
def get_employees_applied_leaves(request):
	
	employee_leaves = employee_applied_leaves.objects.filter(status = 'Pending')
	serializer = get_employee_apllied_leaves(employee_leaves , many = True)
	return Response({'status':status.HTTP_200_OK, 'data':serializer.data},status=status.HTTP_200_OK)

@api_view(('GET',))
def get_employee_applied_leaves(request,id):
	employee_leaves = employee_applied_leaves.objects.prefetch_related('leave_days').filter(id = id)
	result = []
	for leave in employee_leaves:
		session = leave.leave_days.all()
		session_data = create_employee_applied_leaves_days(session,many=True).data
		data = {
			'start_date' : leave.start_date,
			'end_date' : leave.end_date,
			'leave_type' : leave.leave_type,
			'reason' : leave.reason,
			'status' : leave.status,
			'sessions' : session_data,
		}
		result.append(data)
	serializer = get_employee_applied_leave(data = result,many = True)
	
	if serializer.is_valid():
		return Response({'status':status.HTTP_200_OK, 'data':serializer.data},status=status.HTTP_200_OK)
	else:
		return Response({'status':status.HTTP_400_BAD_REQUEST, 'data':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
		
@api_view(('PATCH',))
def update_employee_applied_leaves(request, id):
	data = request.data
	Total_days, leave_balance = check_employee_leave_availability(data)
	try:
		filter_by_status = employee_applied_leave_days.objects.filter(status = 'Pending')
		employee_info = employee_applied_leaves.objects.prefetch_related(Prefetch('leave_days', queryset=filter_by_status)).get(id=id)
	except employee_applied_leaves.DoesNotExist:
		return Response({
			"statuscode": status.HTTP_404_NOT_FOUND,
			"status": "failed",
			"message": "Employee leave request not found"
		})
	employee_session_data = create_employee_applied_leaves_days(employee_info.leave_days.all(), many=True).data
	try:
		if data['status'] == 'Approved':
			for employee_session in employee_session_data:
				attendance_data = {
					'employee_id': data['employee_id'],
					'date': employee_session['leave_date']
				}
				serializer = create_attendance_byinfo_serializer(data = attendance_data)
				if serializer.is_valid():
					attendance = employee_attendance.objects.create(**serializer.validated_data)
					attendance_id = attendance.attendance_id
					attendance_data['attendance_id'] = attendance_id
					attendance_data['status'] = data['leave_type']
					serializer = atttendance_info_post_serializer(data = attendance_data)
					if serializer.is_valid():
						apply_data = serializer.validated_data
						create_attendance_info = employees_attendance_info.objects.create(**apply_data, action_by =1)
					else:
						return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	except:
		pass
	serializer = create_employee_applied_leaves(employee_info, data=data, partial=True)
	employee_leave_balance = employee_leave_balances.objects.get(employee_id=employee_info.employee_id)
	       							##### for calculating the existing total applied leaves #####
	existing_sick_leave = 0
	existing_casual_leave = 0
	for session_data in employee_info.leave_days.all():
		if employee_info.leave_type == "Sick Leave":
			if session_data.session =='Morning' or session_data.session == 'Evening':
				existing_sick_leave += 0.5
			else:
				existing_sick_leave += 1
		if employee_info.leave_type == "Casual Leave":
			if session_data.session =='Morning' or session_data.session == 'Evening':
				existing_casual_leave += 0.5
			else:
				existing_casual_leave += 1

	if serializer.is_valid():
		if Total_days > leave_balance + existing_casual_leave + existing_sick_leave:
			return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"failed","message":"Leave balance is not sufficient"})
		serializer.save()
		if data['leave_type'] == 'Sick Leave':
			if Total_days > existing_sick_leave:
				total = Total_days - existing_sick_leave
				employee_leave_balance.sick_leave = employee_leave_balance.sick_leave - total
			else:
				total = existing_sick_leave - Total_days
				employee_leave_balance.sick_leave = employee_leave_balance.sick_leave + total
		elif data['leave_type'] == 'Casual Leave':
			if Total_days > existing_casual_leave:
				total = Total_days - existing_casual_leave
				employee_leave_balance.casual_leave = employee_leave_balance.casual_leave - total
			else:
				total = existing_casual_leave - Total_days
				employee_leave_balance.casual_leave = employee_leave_balance.casual_leave + total
		employee_leave_balance.save()
		
		return Response({
			"statuscode": status.HTTP_200_OK,
			"status": "success",
			"message": "Employee leave request updated successfully"
		}, status=status.HTTP_200_OK)
	else:
		return Response({
			"statuscode": status.HTTP_400_BAD_REQUEST,
			"status": "failed",
			"errors": serializer.errors
		}, status=status.HTTP_400_BAD_REQUEST)

@api_view(('POST',))
def apply_employee_permission(request):
	check_exist_permission  = check_existing_permission(request.data)
	if check_exist_permission:
		return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","message":"The permission will be applied please update or change time"}, status=status.HTTP_400_BAD_REQUEST)
	serializer = create_applied_permission(data = request.data)
	if serializer.is_valid():
		data = request.data
		validated_data = serializer.validated_data
		employee_permission_balance = employee_leave_balances.objects.get(employee_id = data['employee'])
		start_dt = datetime.strptime(data['start_time'], "%H:%M")
		end_dt = datetime.strptime(data['end_time'], "%H:%M")
		duration = end_dt - start_dt
		time = convert_timedelta_to_time(duration)
		if time <= employee_permission_balance.permissions:
			employee_permission = employee_applied_permissions.objects.create(**validated_data, created_by = 1 , updated_by = 1)
			value = calculate_permission_time(employee_permission_balance.permissions , time)
			employee_permission_balance.permissions = value
			employee_permission_balance.save()
			return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"Permission applied successfully"},status=status.HTTP_201_CREATED)
		else:
			return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","message":"Infuccient permission balance"}, status=status.HTTP_400_BAD_REQUEST)
	else:
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(('PATCH',))
def update_employee_permission(request,id):
	data = request.data
	if data['end_time'] < data['start_time']:
		return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","message":"End date msut be greater"}, status=status.HTTP_400_BAD_REQUEST)
	check_exist_permission  = check_existing_permission(data)
	if check_exist_permission:
		return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","message":"The permission will be applied please update or change time"}, status=status.HTTP_400_BAD_REQUEST)
	applied_permission = employee_applied_permissions.objects.get(permission_id = id)
	employee_permission_balance = employee_leave_balances.objects.get(employee_id = data['employee'])
	time  = time_duration(data['start_time'], data['end_time'])
	previous_duration = calculate_permission_time(applied_permission.end_time ,applied_permission.start_time)
	balance_duration = add_effective_time(employee_permission_balance.permissions, previous_duration)
	if time <= balance_duration:
		serializer = create_applied_permission(applied_permission, partial = True)
		value = calculate_permission_time(balance_duration , time)
		employee_permission_balance.permissions = value
		employee_permission_balance.save()
		return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"Permission applied successfully"},status=status.HTTP_201_CREATED)

	else:
		return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","message":"Infuccient permission balance"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(('GET',))
def get_employees_applied_permissions(request):
	employee_pending_permissions = employee_applied_permissions.objects.filter(status = "Pending")
	serializer = create_applied_permission(employee_pending_permissions, many = True)
	return Response({'status':status.HTTP_200_OK, 'data':serializer.data},status=status.HTTP_200_OK)

@api_view(('GET',))
def get_employee_applied_permissions(request, id):
	employee_applied_permission = employee_applied_permissions.objects.filter(employee = id)
	serializer = create_applied_permission(employee_applied_permission, many = True)
	return Response({'status':status.HTTP_200_OK, 'data':serializer.data},status=status.HTTP_200_OK)