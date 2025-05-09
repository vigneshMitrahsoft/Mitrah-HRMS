from employee.models import employee, employee_salary_info
from company.models import company_Settings
from attendance.models import employees_attendance_info
from holiday.models import holiday
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from rest_framework.decorators import api_view #, permission_classes

@api_view(['GET'])
def generate_payslip(request, id):
	employee_instance = employee.objects.get(employee_id=id)
	print(employee_instance,"employee_instance")
	employee_company = company_Settings.objects.get(company=employee_instance.company_id.company_id)
	print(employee_company,"employee_company")
	print(employee_company.employee_PF,"employee_PF from the employee_company")
	print(employee_company.employee_ESI,"empoyee ESI from the employee_company")
	employee_salary = employee_salary_info.objects.get(employee_id=employee_instance)
	print(employee_salary,"employee_salary")

	# CTC calculation
	ctc = employee_salary.gross_salary + employee_salary.variable_pay
	print(ctc,"ctc")

	# Initial earnings calculation
	basic_pay = ctc * (employee_company.basic_pay / 100)
	print(basic_pay,"basic_pay")
	hra = basic_pay * (employee_company.HRA / 100)
	print(hra,"hra")
	other_allowance = basic_pay * (employee_company.other_allowances / 100)
	print(other_allowance,"other_allowance")

	total_earnings = basic_pay + hra + other_allowance
	print(total_earnings,"total_earnings")

	# Validate total earnings <= CTC
	travel_allowance = 0
	if total_earnings < ctc:
		travel_allowance = ctc - total_earnings
		total_earnings += travel_allowance

	# Deductions
	print(employee_company.employee_PF,"employee_PF percentage")
	print(employee_company.employee_ESI,"employee_ESI percentage")

	employee_pf_deduction = (employee_company.employee_PF / 100) * basic_pay
	print(employee_pf_deduction,"employee_pf_deduction")
	employee_esi_deduction = (employee_company.employee_ESI / 100) * employee_salary.gross_salary
	print(employee_esi_deduction,"employee_esi_deduction")

	# Leave and LOP calculation
	company_audit_date = 31  # TODO: Make dynamic
	today = datetime.today()
	given_date = datetime.strptime(f"{company_audit_date}-{today.month}-{today.year}", "%d-%m-%Y").date()
	start_date = given_date - relativedelta(months=1)
	end_date = given_date

	weekday_count = sum(1 for d in (start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)) if d.weekday() < 5)
	print(weekday_count,"weekday_count")
	holidays = holiday.objects.filter(holiday_date__range=[start_date, end_date])
	print(holidays,"holidays")
	working_days = weekday_count - holidays.count()
	leave_days = employees_attendance_info.objects.filter(date__range=[start_date, end_date], status='Absent').count()
	print(leave_days,"leave_days")

	lop_amount = (employee_salary.gross_salary / working_days) * leave_days
	print(lop_amount,"lop_amount")
	total_deductions = employee_pf_deduction + employee_esi_deduction + lop_amount
	print(total_deductions,"total_deductions")

	# Net salary
	net_pay = total_earnings - total_deductions
	print(net_pay,"net_pay")

	# Final structured payslip
	payslip_data = {
		"employee name": employee_instance.first_name + " " + employee_instance.last_name,
		"employee id": employee_instance.employee_id,
		"employee_email": employee_instance.email,
		"earnings": {
			"basic pay": round(basic_pay, 2),
			"hra": round(hra, 2),
			"allowance": round(other_allowance, 2),
			"travel allowance": round(travel_allowance, 2) if travel_allowance else 0
		},
		"deductions": {
			"pf": round(employee_pf_deduction, 2),
			"esi": round(employee_esi_deduction, 2),
			"lop": round(lop_amount, 2)
		},
		"net pay": round(net_pay, 2)
	}

	return JsonResponse([payslip_data], safe=False)
