from rest_framework.decorators import api_view
from datetime import datetime
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
from django.db.models import Sum

@api_view(('GET',))
def dashboard(request):
	employee_id = request.user.employee_id
	if employee_id:
		try:
			employee_info = employee.objects.get(employee_id=employee_id, is_active=True)
		except employee.DoesNotExist:
			return Response({
				"statuscode": status.HTTP_404_NOT_FOUND,
				"status": "error",
				"message": "Employee not found"
			}, status=status.HTTP_404_NOT_FOUND)
		
		company_id = employee_info.company_id
		if not company_id:
			return Response({
				"statuscode": status.HTTP_404_NOT_FOUND,
				"status": "error",
				"message": "Company not found"
			}, status=status.HTTP_404_NOT_FOUND)

		# Employee Info
		fullname = f"{employee_info.first_name} {employee_info.last_name}"
		email = employee_info.email

		end_date = timezone.now().date()
		start_date = (end_date.replace(day=1) - relativedelta(months=4))#end_date - relativedelta(months=5)

		employee_count = employee.objects.filter(company_id=company_id).count()
		active_employee_count = employee.objects.filter(company_id = company_id, is_active=True).count()
		inactive_employee_count = employee.objects.filter(company_id = company_id, is_active=False).count()
		employee_applied_leave_count = employee_applied_leaves.objects.filter(employee_id__company_id = company_id).count()
		loan_count = LoanDeduction.objects.filter(employee_id__company_id=company_id).count()
		overtime_count = Overtime.objects.filter(employee_id__company_id=company_id).count()

		monthly_employee_counts = (
			employee.objects
			.filter(date_of_joining__range=(start_date, end_date), company_id=company_id)
			.annotate(month=TruncMonth('date_of_joining'))
			.values('month')
			.annotate(count=Count('employee_id'))
			.order_by('month')
		)
		# print('monthly_employee_counts:', monthly_employee_counts)

		# Format for response
		monthly_data = OrderedDict()
		for entry in monthly_employee_counts:
			month_label = entry['month'].strftime('%b %Y')
			monthly_data[month_label] = entry['count']

		pending_loan_count = LoanDeduction.objects.filter(employee_id__company_id=company_id, status='Pending').count()
		print('pending_loan_count:=============>', pending_loan_count)
		approved_loan_count = LoanDeduction.objects.filter(employee_id__company_id=company_id, status='Approved').count()
		print('approved_loan_count:==============>', approved_loan_count)

		# Monthly loan approvals (last 5 months)
		monthly_loan_counts = (
			LoanDeduction.objects
			.filter(approved_date__range=(start_date, end_date), employee_id__company_id=company_id, status='Approved')
			.annotate(month=TruncMonth('approved_date'))
			.values('month')
			.annotate(count=Count('loan_id'))
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
		accepted_loans = LoanDeduction.objects.filter(employee_id__company_id=company_id, status='Accepted')

		# Sum total loan amounts
		total_loan_amount = accepted_loans.aggregate(total=Sum('loan_amount'))['total'] or 0
		print('total_loan_amount:================================>', total_loan_amount)

		# Get all repayments made against those loans
		loan_ids = accepted_loans.values_list('loan_id', flat=True)
		total_repaid_amount = Repayment.objects.filter(loan_id__in=loan_ids).aggregate(total=Sum('amount_paid'))['total'] or 0
		print('total_repaid_amount:===================================>', total_repaid_amount)

		# Calculate amount still to be paid
		due_amount_to_company = total_loan_amount - total_repaid_amount

		# print('active_employee_count:', active_employee_count)
		# print('inactive_employee_count:', inactive_employee_count)
		# print('employee_applied_leave_count:', employee_applied_leave_count)
		# print('loan_count:', loan_count)
		# print('overtime_count:', overtime_count)
		# print('employee_count:', employee_count)

		context = {
			"employee": {
				"fullname": fullname,
				"email": email
			},
			"employees_data": {
				"employee_count": employee_count,
				"count_of_employees":{
					"active_employee_count": active_employee_count,
					"inactive_employee_count": inactive_employee_count
				},
				"analytic_data_of_employees": monthly_data
			},
			"leave_data": {
				"employee_applied_leave_count": employee_applied_leave_count
			},
			"loan_data": {
				"loan_count": loan_count,
				"pending_loan_count": pending_loan_count,
				"approved_loan_count": approved_loan_count,
				"analytic_data_of_loans": loan_monthly_data,
				"total_loan_amount": total_loan_amount,
				"total_repaid_amount": total_repaid_amount,
				"due_amount_to_company": due_amount_to_company
			},
			"overtime_data": {
				"overtime_count": overtime_count
			}
		}
		return Response({
			"statuscode": status.HTTP_200_OK,
			"status": "success",
			"data": context
		}, status=status.HTTP_200_OK)



@api_view(('GET',))
def employeedashboard(request):
	pass