from .models import employee_leave_balances,employee_applied_leave_days
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import create_leavebalance_serializer, get_leavebalance_serializer, create_employee_applied_leaves, create_employee_applied_leaves_days
from attendance.models import employee_applied_leaves


@api_view(('POST',))
def create_employee_leave_balances(request):
	data  = {
		'employee_id': 16,
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
		print('errors', serializer.errors)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
@api_view(('GET',))
def get_employees_leave_balances(request):
	try:
		data = employee_leave_balances.objects.all()
		print(data)
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
	print("employee_info---->",employee_leave_info['employee_id'])
	Total_days = 0
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
		}
		serializer = create_employee_applied_leaves(data = data)
		if serializer.is_valid():
			data = serializer.validated_data
			employee_applied_leave = employee_applied_leaves.objects.create(**data , action_by = 1)	
			for session in employee_leave_info['sessions']:
				print("session----->",session)
				data = {
					'applied_leave_request_id' : employee_applied_leave.id,
					'leave_date' : session['date'],
					'session' : session['session'],
					'comment' : session['comment'],
					'status' : "Pending"
				}
				serializer = create_employee_applied_leaves_days(data = data)
				if serializer.is_valid():
					data = serializer.validated_data
					employee_applied_leave_days.objects.create(**data , created_by = 1, updated_by = 1)
					if session['session'] == "Morning" or session['session'] == "Evening":
						if employee_leave_info ['leave_type'] == "Sick Leave":
							employee_leave_balance.sick_leave -= 0.5
						elif employee_leave_info ['leave_type'] == "Casual Leave":
							employee_leave_balance.casual_leave -= 0.5
						employee_leave_balance.save()
					elif session['session'] == "Full Day":
						if employee_leave_info ['leave_type'] == "Sick Leave":
							employee_leave_balance.sick_leave -= 1
						elif employee_leave_info ['leave_type'] == "Casual Leave":
							employee_leave_balance.casual_leave -= 1
						employee_leave_balance.save()
			return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"Leave applied successfully"},status=status.HTTP_201_CREATED)
		else:
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)