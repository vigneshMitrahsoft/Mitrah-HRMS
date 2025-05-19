from datetime import timedelta
from rest_framework import  serializers
from employee.models import employee
from .models import employee_leave_balances, employee_applied_leave_days, employee_applied_leaves,employee_applied_permissions
from django.db.models import Prefetch


class create_leavebalance_serializer(serializers.ModelSerializer):
	class Meta:
		model = employee_leave_balances
		fields = "__all__"
class get_leavebalance_serializer(serializers.ModelSerializer):
	
	class Meta:
		model = employee_leave_balances
		fields = "__all__"

class create_employee_applied_leaves_days(serializers.Serializer):
	# applied_leave_request_id = serializers.PrimaryKeyRelatedField(queryset=employee_applied_leaves.objects.all(), required=True)
	leave_date = serializers.DateField(required = True)
	session = serializers.CharField(required = True)
	comment = serializers.CharField(required = True)
	status = serializers.CharField(default = "Pending")

class create_employee_applied_leaves(serializers.Serializer):
	employee_id = serializers.PrimaryKeyRelatedField(queryset=employee.objects.all(), required=True)
	start_date = serializers.DateField(required = True)
	end_date = serializers.DateField(required = True)
	leave_type = serializers.CharField(required = True)
	reason = serializers.CharField(required = True)
	status = serializers.CharField(required = True)
	sessions = create_employee_applied_leaves_days(many=True)
	def validate(self, data):
		error = {}
		if data['start_date'] > data['end_date']: 
			# raise serializers.ValidationError( "End date should be greater than start date")
			error['date_error'] = "End date should be greater than start date"
		session_dates = [session['leave_date'] for session in data['sessions']]
		session_dates_set = set(session_dates)
		print("session_sate---->",session_dates_set, type(session_dates_set))
		total_days = (data['end_date'] - data['start_date']).days + 1
		expected_dates_set = {
			(data['start_date'] + timedelta(days=i)) for i in range(total_days)
		}
		print("exp session_sate---->",expected_dates_set, type(expected_dates_set))

		# Compare expected vs. actual session dates
		if session_dates_set != expected_dates_set:
			error['session_date_error'] = (
				"You must apply leave for all dates from start_date to end_date."
            )
		check_dates =[]
		# sick_leave = 0
		# casual_leave = 0
		for session_data in data['sessions']:
			if not (data['start_date'] <= session_data['leave_date'] <= data['end_date']):
				error['session_data_error'] = "Leave date should be between start date and end date"
			
			elif session_data['leave_date'] in check_dates:
				error['session_data_error'] = "Leave date should be unique"
			else:
				check_dates.append(session_data['leave_date'])
			leave_data = employee_applied_leaves.objects.filter(employee_id=data['employee_id'].employee_id, leave_days__leave_date=session_data['leave_date']).exclude(leave_days__status='Cancelled')
			if leave_data.exists():
				for leave in leave_data:
					entry = leave.leave_days.all()
					for entry in entry:
						print('entry:', entry.session)
						if entry.session == session_data['session']:
							error['session_data_error'] = "You have already applied for this date"
						else:
							if entry.status == 'Pending':
								error['session_data_error'] = "You have already applied for this date, please update the existing request."
		if error:	
			raise serializers.ValidationError(error)
		
		return data

	def update(self, instance, validated_data):

		sessions_data = validated_data.pop('sessions', [])
		for attr, value in validated_data.items():
			setattr(instance, attr, value)
		instance.save()

		existing_leave_days = instance.leave_days.all()
		existing_leave_dates = [session['leave_date'] for session in sessions_data]  
		for leave_day in existing_leave_days:
			if leave_day.leave_date not in existing_leave_dates:
				leave_day.status = 'Cancelled'  
				leave_day.save()
		for session_data in sessions_data:
			leave_day = instance.leave_days.filter(leave_date=session_data['leave_date'], session=session_data['session'], status = 'Pending').first()
			leave_day_diff_session = instance.leave_days.filter(leave_date=session_data['leave_date'] , status = 'Pending').first()
			if leave_day:
				leave_day.comment = session_data['comment']
				leave_day.status = "Pending"
				leave_day.save()
			
			elif leave_day_diff_session:
				leave_day_diff_session.comment = session_data['comment']
				leave_day_diff_session.session = session_data['session']
				leave_day_diff_session.save()

			else:
				employee_applied_leave_days.objects.create(
					applied_leave_request_id=instance,  
					leave_date=session_data['leave_date'],
					session=session_data['session'],
					comment=session_data['comment'],
					status='Pending' 
				)

		return instance
		
class get_employee_apllied_leaves(serializers.ModelSerializer):

	class Meta:
		model = employee_applied_leaves
		fields ='__all__'

class get_employee_applied_leave(serializers.Serializer):
	start_date = serializers.DateField(required = True)
	end_date = serializers.DateField(required = True)
	leave_type = serializers.CharField(required = True)
	reason = serializers.CharField(required = True)
	status = serializers.CharField(required = True)
	sessions = create_employee_applied_leaves_days(many=True)

class create_applied_permission(serializers.ModelSerializer):

	class Meta:
		model = employee_applied_permissions
		fields = "__all__"

	def validate(self, data):
		if data['end_time'] < data['start_time']:
			raise serializers.ValidationError("enddate must be greater than start date")
		return data
	
class update_applied_permission(serializers.ModelSerializer):
	class Meta:
		model = employee_applied_permissions
		fields = "__all__"