from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
from employee.models import employee
from leave.models import employee_applied_leaves
from loan.models import LoanDeduction, Repayment
from overtime.models import Overtime
from django.db.models.functions import TruncMonth
from django.db.models import Count
from collections import OrderedDict
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import ExpressionWrapper, F, DurationField, Sum
from rest_framework.permissions import IsAuthenticated
from auth.views import IsAuthorized
from rest_framework.exceptions import APIException
from leave.models import employee_leave_balances
from payslips.models import Payslip


def check_employee_exists(employee_id):
	"""
	Check if the employee exists in the database.
	"""
	try:
		employee_info = employee.objects.get(employee_id=employee_id, is_active=True)
	except employee.DoesNotExist:
		raise APIException(detail={"statuscode": 404, "status": "error", "message": "Loan not found"})
	return employee_info

@api_view(('GET',))
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr'])
def dashboard(request):
	employee_id = request.user.employee_id
	if employee_id:
		employee_info = check_employee_exists(employee_id)
		company_id = employee_info.company_id
		if not company_id:
			return Response({"statuscode": status.HTTP_404_NOT_FOUND, "status": "error", "message": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

		# Employee Info
		fullname = f"{employee_info.first_name} {employee_info.last_name}"
		email = employee_info.email

		end_date = timezone.now().date()
		start_date = (end_date.replace(day=1) - relativedelta(months=4))#end_date - relativedelta(months=5)

		employee_count = employee.objects.filter(company_id=company_id).count()
		active_employee_count = employee.objects.filter(company_id = company_id, is_active=True).count()
		inactive_employee_count = employee.objects.filter(company_id = company_id, is_active=False).count()
		employee_applied_leave_count = employee_applied_leaves.objects.filter(employee_id__company_id = company_id).count()
		loan_count = LoanDeduction.objects.filter(employee_id__company_id = company_id).count()
		overtime_count = Overtime.objects.filter(employee_id__company_id = company_id).count()

		employee_leave_balance = employee_leave_balances.objects.get(employee_id = employee_info, employee_id__company_id = company_id)
		sick_leave = employee_leave_balance.sick_leave
		casual_leave = employee_leave_balance.casual_leave
		permission_hours = employee_leave_balance.permission_hours
		compensation_leave = employee_leave_balance.compensation_leave

		active_loan = LoanDeduction.objects.filter(employee_id = employee_info, status = 'Accepted', employee_id__company_id = company_id).count()
		total_outstanding_loan = LoanDeduction.objects.filter(employee_id = employee_info, status = 'Accepted').aggregate(total = Sum('loan_amount'))['total'] or 0
		total_repaid_loan = Repayment.objects.filter(loan_id__employee_id = employee_info).aggregate(total = Sum('amount_paid'))['total'] or 0
		due_amount = total_outstanding_loan - total_repaid_loan

		latest_pay_slip = Payslip.objects.filter(employee_id = employee_info, employee_id__company_id = company_id).order_by('-created_at').first()
		payslip_data = {
			"payslip_month": latest_pay_slip.month if latest_pay_slip else None,
			"payslip_year": latest_pay_slip.year if latest_pay_slip else None,
			"net_salary": latest_pay_slip.net_pay if latest_pay_slip else None,
		}

		monthly_overtime = (
			Overtime.objects
			.filter(
				employee_id = employee_info,
				status = 'Approved',
				is_deleted = False,
				date__range = (start_date, end_date)
			)
			.annotate(
				month = TruncMonth('date'),
				duration = ExpressionWrapper(
					F('end_time') - F('start_time'),
					output_field = DurationField()
				)
			)
			.values('month')
			.annotate(
				total_duration = Sum('duration')
			)
			.order_by('month')
		)

		# Initialize chart data with zero values for all 5 months
		overtime_chart_data = OrderedDict()
		current = start_date.replace(day=1)
		while current <= end_date:
			label = current.strftime('%b %Y')
			overtime_chart_data[label] = 0
			current += relativedelta(months=1)

		# Populate actual values
		for entry in monthly_overtime:
			month_label = entry['month'].strftime('%b %Y')
			total_duration = entry['total_duration']
			if total_duration:
				total_hours = total_duration.total_seconds() / 3600
				overtime_chart_data[month_label] = round(total_hours, 2)

		monthly_employee_counts = (
			employee.objects
			.filter(date_of_joining__range = (start_date, end_date), company_id = company_id)
			.annotate(month = TruncMonth('date_of_joining'))
			.values('month')
			.annotate(count = Count('employee_id'))
			.order_by('month')
		)

		monthly_employee_leavers = (
		employee.objects
		.filter(updated_at__range = (start_date, end_date), company_id = company_id, is_active = False)
		.annotate(month = TruncMonth('updated_at'))
		.values('month')
		.annotate(count = Count('employee_id'))
		.order_by('month')
		)

		joining_leaving_trend = OrderedDict()

		# Initialize with 0s
		current = start_date.replace(day=1)
		while current <= end_date:
			label = current.strftime('%b %Y')
			joining_leaving_trend[label] = {
				'joined': 0,
				'left': 0
			}
			current += relativedelta(months=1)

		# Format for response
		for entry in monthly_employee_counts:
			month_label = entry['month'].strftime('%b %Y')
			joining_leaving_trend[month_label]['joined'] = entry['count']

		for entry in monthly_employee_leavers:
			month_label = entry['month'].strftime('%b %Y')
			joining_leaving_trend[month_label]['left'] = entry['count']
		

		pending_loan_count = LoanDeduction.objects.filter(employee_id__company_id = company_id, status = 'Pending').count()
		approved_loan_count = LoanDeduction.objects.filter(employee_id__company_id = company_id, status = 'Accepted').count()

		# Monthly loan approvals (last 5 months)
		monthly_loan_counts = (
			LoanDeduction.objects
			.filter(approved_date__range = (start_date, end_date), employee_id__company_id = company_id, status = 'Accepted')
			.annotate(month = TruncMonth('approved_date'))
			.values('month')
			.annotate(count = Count('loan_id'))
			.order_by('month')
		)

		# Format monthly loan data
		loan_monthly_data = OrderedDict()

		# Ensure all months from start_date to end_date are covered
		current = start_date.replace(day=1)
		while current <= end_date:
			label = current.strftime('%b %Y')
			loan_monthly_data[label] = 0
			current += relativedelta(months=1)

		# Populate actual counts
		for entry in monthly_loan_counts:
			label = entry['month'].strftime('%b %Y')
			loan_monthly_data[label] = entry['count']

		# Get all accepted loans for the company
		accepted_loans = LoanDeduction.objects.filter(employee_id__company_id = company_id, status='Accepted')

		# Sum total loan amounts
		total_loan_amount = accepted_loans.aggregate(total = Sum('loan_amount'))['total'] or 0

		# Get all repayments made against those loans
		loan_ids = accepted_loans.values_list('loan_id', flat = True)
		total_repaid_amount = Repayment.objects.filter(loan_id__in = loan_ids).aggregate(total = Sum('amount_paid'))['total'] or 0

		# Calculate amount still to be paid
		due_amount_to_company = total_loan_amount - total_repaid_amount

		monthly_leave_applications = (
			employee_applied_leaves.objects
			.filter(employee_id = employee_info, status = 'Approved')
			.annotate(month = TruncMonth('start_date'))
			.values('month')
			.annotate(count = Count('id'))
			.order_by('month')
		)

		leave_application_chart_data = OrderedDict()
		for item in monthly_leave_applications:
			label = item['month'].strftime('%b %Y')
			leave_application_chart_data[label] = item['count']


		context = {
			"employee": {
				"employee_details":{
					"fullname": fullname,
					"email": email	
				},
				"employee_leave_balance": {
					"sick_leave": sick_leave,
					"casual_leave": casual_leave,
					"permission_hours": permission_hours,
					"compensation_leave": compensation_leave
				},
				"loan_data": {
					"active_loan": active_loan,
					"total_outstanding_loan": total_outstanding_loan,
					"total_repaid_loan": total_repaid_loan,
					"due_amount": due_amount
				},
				"payslip_data": {
					"payslip_month": payslip_data["payslip_month"],
					"payslip_year": payslip_data["payslip_year"],
					"net_salary": payslip_data["net_salary"]
				},
				"overtime_chart_data": overtime_chart_data,
				"leave_application_chart_data": leave_application_chart_data
			},
			"employees_data": {
				"employee_count": employee_count,
				"count_of_employees":{
					"active_employee_count": active_employee_count,
					"inactive_employee_count": inactive_employee_count
				},
				"analytic_data_of_employees": joining_leaving_trend
			},
			"leave_data": {
				"employee_applied_leave_count": employee_applied_leave_count
			},
			"loan_data": {
				"loan_count": loan_count,
				"count_of_loans":{
					"pending_loan_count": pending_loan_count,
					"approved_loan_count": approved_loan_count,		
				},
				"analytic_data_of_loans": loan_monthly_data,
				"total_loan_amount": total_loan_amount,   
				"total_repaid_amount": total_repaid_amount,
				"due_amount_to_company": due_amount_to_company
			},
			"overtime_data": {
				"overtime_count": overtime_count
			}
		}
		return Response({"statuscode": status.HTTP_200_OK, "status": "success", "data": context}, status=status.HTTP_200_OK)

@api_view(('GET',))
def employee_dashboard(request):
	employee_id = request.user.employee_id
	if employee_id:
		employee_info = check_employee_exists(employee_id)
		company_id = employee_info.company_id
		if not company_id:
			return Response({"statuscode": status.HTTP_404_NOT_FOUND, "status": "error", "message": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
		
		# Employee Info
		fullname = f"{employee_info.first_name} {employee_info.last_name}"
		email = employee_info.email

		employee_leave_balance = employee_leave_balances.objects.get(employee_id = employee_info, employee_id__company_id = company_id)
		sick_leave = employee_leave_balance.sick_leave
		casual_leave = employee_leave_balance.casual_leave
		permission_hours = employee_leave_balance.permission_hours
		compensation_leave = employee_leave_balance.compensation_leave

		active_loan = LoanDeduction.objects.filter(employee_id = employee_info, status = 'Accepted', employee_id__company_id = company_id).count()
		total_outstanding_loan = LoanDeduction.objects.filter(employee_id = employee_info, status = 'Accepted').aggregate(total = Sum('loan_amount'))['total'] or 0
		total_repaid_loan = Repayment.objects.filter(loan_id__employee_id = employee_info).aggregate(total = Sum('amount_paid'))['total'] or 0
		due_amount = total_outstanding_loan - total_repaid_loan    

		latest_pay_slip = Payslip.objects.filter(employee_id = employee_info, employee_id__company_id = company_id).order_by('-created_at').first()
		payslip_data = {
			"payslip_month": latest_pay_slip.month if latest_pay_slip else None,
			"payslip_year": latest_pay_slip.year if latest_pay_slip else None,
			"net_salary": latest_pay_slip.net_pay if latest_pay_slip else None,
		}

		end_date = timezone.now().date()
		start_date = end_date.replace(day=1) - relativedelta(months=4)	
		
		monthly_overtime = (
			Overtime.objects
			.filter(
				employee_id = employee_info,
				status = 'Approved',
				is_deleted = False,
				date__range = (start_date, end_date)
			)
			.annotate(
				month = TruncMonth('date'),
				duration = ExpressionWrapper(
					F('end_time') - F('start_time'),
					output_field = DurationField()
				)
			)
			.values('month')
			.annotate(
				total_duration = Sum('duration')
			)
			.order_by('month')
		)

		# Initialize chart data with zero values for all 5 months
		overtime_chart_data = OrderedDict()
		current = start_date.replace(day=1)
		while current <= end_date:
			label = current.strftime('%b %Y')
			overtime_chart_data[label] = 0
			current += relativedelta(months=1)

		# Populate actual values
		for entry in monthly_overtime:
			month_label = entry['month'].strftime('%b %Y')
			total_duration = entry['total_duration']
			if total_duration:
				total_hours = total_duration.total_seconds() / 3600
				overtime_chart_data[month_label] = round(total_hours, 2)

		monthly_leave_applications = (
			employee_applied_leaves.objects
			.filter(employee_id = employee_info, status = 'Approved')
			.annotate(month = TruncMonth('start_date'))
			.values('month')
			.annotate(count = Count('id'))
			.order_by('month')
		)

		leave_application_chart_data = OrderedDict()
		for item in monthly_leave_applications:
			label = item['month'].strftime('%b %Y')
			leave_application_chart_data[label] = item['count']

		context = {
			"employee": {
				"fullname": fullname,
				"email": email
			},
			"employee_leave_balance": {
				"sick_leave": sick_leave,
				"casual_leave": casual_leave,
				"permission_hours": permission_hours,
				"compensation_leave": compensation_leave
			},
			"loan_data": {
				"active_loan": active_loan,
				"total_outstanding_loan": total_outstanding_loan,
				"total_repaid_loan": total_repaid_loan,
				"due_amount": due_amount
			},
			"payslip_data": {
				"payslip_month": payslip_data["payslip_month"],
				"payslip_year": payslip_data["payslip_year"],
				"net_salary": payslip_data["net_salary"]
			},
			"overtime_chart_data": overtime_chart_data,
			"leave_application_chart_data": leave_application_chart_data
		}

		return Response({"statuscode": status.HTTP_200_OK, "status": "success", "data": context}, status=status.HTTP_200_OK)
