from auth.views import IsAuthorized
from .models import *
from leave.models import employee_applied_leaves
from rest_framework.response import Response
# from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .serializers import attendance_entry_model, attendance_entry_serializer,create_attendance_serializer,attendance_info_serializer,atttendance_info_post_serializer, entries_serializer,get_employee_attendance_serializer,create_attendance_byinfo_serializer,get_attendance_info_serializer
from datetime import date,datetime,time, timedelta
from django.utils import timezone
from django.db import connection
from django.db.models import Prefetch
from rest_framework.permissions import IsAuthenticated


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
@permission_classes((IsAuthenticated,))
def check_in_entry(request):
	token_user_id = request.user.employee_id  
	employee_id = token_user_id           
	today = date.today()
	current_date_time = datetime.now()
	try:
		today_entry = employee_attendance.objects.get(employee_id = employee_id, date = today)
		if today_entry.check_in is None:
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
			employee_checkin = employee_attendance.objects.create(**data,created_by = token_user_id,updated_by = token_user_id)
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
				# need to add the present condition (In future)
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
				employees_attendance_info.objects.create(**serializer.validated_data , action_by = token_user_id)
	return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"checkin successfully"},status=status.HTTP_201_CREATED)

@api_view(('POST',))
@permission_classes((IsAuthenticated,))
def check_out_entry(request):
	token_user_id = request.user.employee_id
	employee_id = token_user_id
	today = date.today()
	current_date_time = datetime.now()
	try:
		today_entry = employee_attendance.objects.get(employee_id = employee_id, date = today)
		if today_entry.check_out is not None:
			return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","message":"You already checkout please checkin"},status=status.HTTP_400_BAD_REQUEST)
		else:
			today_entry.check_out = current_date_time
			check_in_hours = today_entry.check_in.replace(tzinfo=None)
			total_time = current_date_time - check_in_hours
			today_entry.total_hours = convert_timedelta_to_time(total_time)
			today_entry.save()
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

# @api_view(('POST',))
# @permission_classes((IsAuthenticated,))
# def get_employee_attendance(request,id):
# 	# NOTE:Before call the api you need to run the get_employee_attendance sql file in db_schema into the postgres db then call the api
# 	data = request.data
# 	query = "SELECT * FROM fn_get_employee_attendances(%s, %s, %s)"
# 	with connection.cursor() as cursor:
# 		cursor.execute(query,[id,data['month'],data['year']])
# 		result = cursor.fetchall()
# 	column_names = [
# 	'date', 'day','weekend','attendance_status', 'leave_status',
# 	'check_in', 'check_out', 'effective_hours', 'total_hours', 'session', 'leave_type', 'attendance_id','holiday_occasion','permission_start_time','permission_end_time'
# 	]
# 	result_dict = [
# 			dict(zip(column_names, row)) for row in result
# 	]
# 	for result in result_dict:
# 		result["check_in"] = result["check_in"].strftime("%Y-%m-%d:%H:%M:%S") if result["check_in"] else "00:00:00"
# 		result["check_out"] = result["check_out"].strftime("%Y-%m-%d:%H:%M:%S") if result["check_out"] else "00:00:00" 
# 	serializer = get_employee_attendance_serializer(result_dict,many = True)

# 	return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serializer.data},status=status.HTTP_200_OK)

@api_view(('POST',))
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr'])
def create_employee_attendance_info(request):
	token_user_id = request.user.employee_id
	serializer = create_attendance_byinfo_serializer(data = request.data)
	if serializer.is_valid():
		try:
			attendance_info = employee_attendance.objects.get(employee_id = request.data['employee_id'],date = request.data['date'])
		except employee_attendance.DoesNotExist:
			attendance = employee_attendance.objects.create(**serializer.validated_data, created_by = token_user_id, updated_by = token_user_id)
			attendance_id = attendance.attendance_id
			request.data['attendance_id'] = attendance_id
			serializer = atttendance_info_post_serializer(data = request.data)
			if serializer.is_valid():
				data = serializer.validated_data
				create_attendance_info = employees_attendance_info.objects.create(**data, action_by = token_user_id)
				return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"created successfully"},status=status.HTTP_201_CREATED)
			else:
				return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
			
		return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","detail": "Employee_attendance already exist."}, status=status.HTTP_400_BAD_REQUEST)
	else:
		return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","detail": "Employee doesnot exist."}, status=status.HTTP_400_BAD_REQUEST)
		
@api_view(('PATCH',))
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr'])
def update_employee_attendance_info(request):
	token_user_id = request.user.employee_id
	id = request.data['employee_id']
	attendance_id = request.data['attendance_id']
	try:
		employee_data = employees_attendance_info.objects.get(employee_id = id, attendance_id = attendance_id)
	except employee_data.DoesNotExist:
		return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","detail": "Employee_attendance_info not found."}, status=status.HTTP_404_NOT_FOUND)
	serializer = attendance_info_serializer(employee_data, data=request.data, partial=True)
	if serializer.is_valid():
		serializer.save(action_by = token_user_id) 
		return Response({"statuscode":status.HTTP_200_OK,"status":"success","message":"updated successfully"},status=status.HTTP_200_OK)
	
	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(('PATCH',))
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr'])
def update_employee_attendance_entries(request,id):
	token_user_id = request.user.employee_id
	data = request.data
	if 'check_in' not in data and 'check_out' not in data:
		return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","detail": "Please provide checkin or checkout time"}, status=status.HTTP_404_NOT_FOUND) 
	today_entry = attendance_entries.objects.get(entry_id = id)
	if 'check_in' in data:
		check_in_date = today_entry.checkin_entry
		update_checkin_date = data['check_in'].strip().replace(".", ":").split(":")
		hour = int(update_checkin_date[0])
		minute = int(update_checkin_date[1])
		try:
			second = int(update_checkin_date[2])
		except:
			second = 0
		check_in_date = check_in_date.replace(hour = hour, minute = minute , second = second)
		today_entry.checkin_entry = check_in_date       
		today_entry.save()
	if 'check_out' in data:
		check_out_date = today_entry.checkout_entry
		update_checkout_date = data['check_out'].strip().replace(".", ":").split(":")
		hour = int(update_checkout_date[0])
		minute = int(update_checkout_date[1])
		try:
			second = int(update_checkout_date[2])
		except:
			second = 0
		check_out_date = check_out_date.replace(hour = hour, minute = minute , second = second)
		today_entry.checkout_entry = check_out_date      
		today_entry.save()

	employee_id = attendance_entries.objects.filter(attendance_id = today_entry.attendance_id).order_by('entry_id')
	
	attendance_id = today_entry.attendance_id
	employee_attendance_data = employee_attendance.objects.get(attendance_id = attendance_id.attendance_id)
	
	for emp in employee_id:
		try:
			time_difference = emp.checkout_entry - emp.checkin_entry
			effective_hours_entries = convert_timedelta_to_time(time_difference)
		except:
			effective_hours_entries = time(0,0,0)
		if emp == employee_id[0]:
			total_effective_hours = effective_hours_entries 
			employee_attendance_data.check_in = emp.checkin_entry
			employee_attendance_data.save(updated_by = token_user_id)
			

		elif emp.entry_id == employee_id.last().entry_id:
			total_effective_hours = add_effective_time(total_effective_hours,effective_hours_entries)
			employee_attendance_data.check_out = emp.checkout_entry
			employee_attendance_data.save(updated_by = token_user_id)
			
		else:
			total_effective_hours = add_effective_time(total_effective_hours,effective_hours_entries)
		
	employee_attendance_data.effective_hours = total_effective_hours
	total_hours = employee_attendance_data.check_out - employee_attendance_data.check_in
	today_entry = convert_timedelta_to_time(total_hours)
	employee_attendance_data.total_hours = today_entry
	employee_attendance_data.save(updated_by = token_user_id)
	return Response({"statuscode":status.HTTP_200_OK,"status":"success","message":"updated successfully"},status=status.HTTP_200_OK)

@api_view(('GET',))
@permission_classes((IsAuthenticated,))
def get_employee_attendance_report(request,id):
	try:
		if request.data['date']:
			filter_date = request.data['date']
	except:
		filter_date = date.today()
	filter_by_date = employee_attendance.objects.prefetch_related('attendanceid').filter(employee_id = id, date = filter_date)
	employee_info = employee.objects.prefetch_related(Prefetch('employeeid', queryset=filter_by_date),'attendanceinfo_employeeid').get(employee_id = id)
	try:
		attendance_data = employee_info.employeeid.all()
		attendance_entries = attendance_data[0].attendanceid.all()
		attendance_info = employee_info.attendanceinfo_employeeid.all()
	except:
		return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","message":"Employee doesnot checkin"},status=status.HTTP_400_BAD_REQUEST)
	entry_serializer = attendance_entry_model(attendance_entries, many = True)

	data = {
		'employee_id':employee_info.employee_id,
		'first_name':employee_info.first_name,
		'last_name':employee_info.last_name,
		'status' : attendance_info[0].status,
		'check_in' : attendance_data[0].check_in,
		'check_out' : attendance_data[0].check_out,
		'effective_hours' : attendance_data[0].effective_hours,
		'total_hours' : attendance_data[0].total_hours,
		'entries': entry_serializer.data
	}
	serializer = get_attendance_info_serializer(data = data)
	if serializer.is_valid():
		return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serializer.data},status=status.HTTP_200_OK)
	else:
		return Response({"statuscode":status.HTTP_400_BAD_REQUEST,"status":"Failed","data":serializer.errors},status=status.HTTP_400_BAD_REQUEST)

@api_view(('GET',))
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr'])
def get_all_employee_attendance_report(request):
	filter_by_date = employee_attendance.objects.prefetch_related('attendanceid').filter(date = date.today())
	employees_info = employee.objects.prefetch_related(
		Prefetch('employeeid', queryset=filter_by_date),
		'attendanceinfo_employeeid'
	).all().order_by('employee_id')

	results = []
	for employee_info in employees_info:
		attendance_data = employee_info.employeeid.all()
		attendance_info = employee_info.attendanceinfo_employeeid.all()
		if attendance_data.exists() and attendance_info.exists():
			attendance_entries = attendance_data[0].attendanceid.all()
			entry_serializer = attendance_entry_model(attendance_entries, many=True)
			data = {
				'employee_id': employee_info.employee_id,
				'first_name': employee_info.first_name,
				'last_name': employee_info.last_name,
				'status': attendance_info[0].status,
				'check_in': attendance_data[0].check_in,
				'check_out': attendance_data[0].check_out,
				'effective_hours': attendance_data[0].effective_hours,
				'total_hours': attendance_data[0].total_hours,
				'entries': entry_serializer.data
			}
			results.append(data)
		else:
			data = {
				'employee_id': employee_info.employee_id,
				'first_name': employee_info.first_name,
				'last_name': employee_info.last_name,
				'status': None,
				'check_in': None,
				'check_out': None,
				'effective_hours': None,
				'total_hours': None,
				'entries': []
			}
			results.append(data)

	serializer = get_attendance_info_serializer(data=results, many=True)
	if serializer.is_valid():
		return Response({"statuscode": status.HTTP_200_OK, "status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
	else:
		return Response({"statuscode": status.HTTP_400_BAD_REQUEST, "status": "Failed", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
	



# from collections import defaultdict

# # Step 1: Group rows by date
# grouped = defaultdict(list)
# for row in result:
#     row_dict = dict(zip(column_names, row))
#     grouped[row_dict['date']].append(row_dict)

# # Step 2: Merge rows per date
# merged_results = []
# for date, items in grouped.items():
#     base = items[0].copy()
#     permissions = []
#     for item in items:
#         permissions.append({
#             "start_time": item['permission_start_time'],
#             "end_time": item['permission_end_time']
#         })
#     base["permissions"] = permissions
#     merged_results.append(base)

from collections import defaultdict
from datetime import datetime

@api_view(('POST',))
@permission_classes((IsAuthenticated,))
def get_employee_attendance(request, id):
	data = request.data
	query = "SELECT * FROM fn_get_employee_attendances(%s, %s, %s)"
	with connection.cursor() as cursor:
		cursor.execute(query, [id, data['month'], data['year']])
		result = cursor.fetchall()

	column_names = [
		'date', 'day', 'weekend', 'attendance_status', 'leave_status',
		'check_in', 'check_out', 'effective_hours', 'total_hours',
		'session', 'leave_type', 'attendance_id', 'holiday_occasion',
		'permission_start_time', 'permission_end_time'
	]

	raw_results = [dict(zip(column_names, row)) for row in result]

	# Group by date + session (if needed)
	grouped_data = defaultdict(lambda: {
	'permissions': [],
	'leaves': [],
	'date': None,
	'day': None,
	'is_week_off': None,
	'attendance_status': '',
	'leave_status': '',
	'check_in': "00:00:00",
	'check_out': "00:00:00",
	'effective_hours': "00:00:00",
	'total_hours': "00:00:00",
	'session': '',
	'leave_type': '',
	'attendance_id': None,
	'holiday_occasion': None,
	})
	for entry in raw_results:
		key = entry['date']
		group = grouped_data[key]

		group['date'] = entry['date']
		group['day'] = entry['day']
		group['is_week_off'] = entry['weekend']
		group['attendance_status'] = entry['attendance_status']
		group['check_in'] = entry['check_in'].strftime("%Y-%m-%d:%H:%M:%S") if entry['check_in'] else "00:00:00"
		group['check_out'] = entry['check_out'].strftime("%Y-%m-%d:%H:%M:%S") if entry['check_out'] else "00:00:00"
		group['effective_hours'] = entry['effective_hours']
		group['total_hours'] = entry['total_hours']
		group['attendance_id'] = entry['attendance_id']
		group['holiday_occasion'] = entry['holiday_occasion']

		# Append permissions
		if entry['permission_start_time'] or entry['permission_end_time']:
			group['permissions'].append({
				'start_time': entry['permission_start_time'],
				'end_time': entry['permission_end_time']
			})

		# Append leaves
		if entry['session'] or entry['leave_type']:
			group['leaves'].append({
				'session': entry['session'],
				'leave_type': entry['leave_type']
			})

		# Optionally: leave status/type from the first non-empty entry
		if not group['leave_status'] and entry['leave_status']:
			group['leave_status'] = entry['leave_status']
		if not group['leave_type'] and entry['leave_type']:
			group['leave_type'] = entry['leave_type']

	final_result = list(grouped_data.values())

	serializer = get_employee_attendance_serializer(final_result, many=True)
	return Response({
		"statuscode": status.HTTP_200_OK,
		"status": "success",
		"data": serializer.data
	}, status=status.HTTP_200_OK)
