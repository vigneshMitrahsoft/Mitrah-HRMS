import string
from employee.models import employee, employee_salary_info
from company.models import company_Settings
from attendance.models import employees_attendance_info
from holiday.models import holiday
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from loan.models import LoanDeduction #, permission_classes
from payslips.models import Payslip
from payslips.serializer import PayslipStatusUpdateSerializer
from taxdeduction.api import calculate_employee_tax_deduction
from rest_framework.exceptions import APIException
# @api_view(['GET'])
# def generate_payslip(request, id):
# 	employee_instance = employee.objects.get(employee_id=id)
# 	print(employee_instance,"employee_instance")
# 	employee_company = company_Settings.objects.get(company=employee_instance.company_id.company_id)
# 	print(employee_company,"employee_company")
# 	print(employee_company.employee_PF,"employee_PF from the employee_company")
# 	print(employee_company.employee_ESI,"empoyee ESI from the employee_company")
# 	employee_salary = employee_salary_info.objects.get(employee_id=employee_instance)
# 	print(employee_salary,"employee_salary")

# 	# CTC calculation
# 	ctc = employee_salary.gross_salary + employee_salary.variable_pay
# 	print(ctc,"ctc")

# 	# Initial earnings calculation
# 	basic_pay = ctc * (employee_company.basic_pay / 100)
# 	print(basic_pay,"basic_pay")
# 	hra = basic_pay * (employee_company.HRA / 100)
# 	print(hra,"hra")
# 	other_allowance = basic_pay * (employee_company.other_allowances / 100)
# 	print(other_allowance,"other_allowance")

# 	total_earnings = basic_pay + hra + other_allowance
# 	print(total_earnings,"total_earnings")

# 	# Validate total earnings <= CTC
# 	travel_allowance = 0
# 	if total_earnings < ctc:
# 		travel_allowance = ctc - total_earnings
# 		total_earnings += travel_allowance

# 	# Deductions
# 	print(employee_company.employee_PF,"employee_PF percentage")
# 	print(employee_company.employee_ESI,"employee_ESI percentage")

# 	employee_pf_deduction = (employee_company.employee_PF / 100) * basic_pay
# 	print(employee_pf_deduction,"employee_pf_deduction")
# 	employee_esi_deduction = (employee_company.employee_ESI / 100) * employee_salary.gross_salary
# 	print(employee_esi_deduction,"employee_esi_deduction")

# 	# Leave and LOP calculation
# 	company_audit_date = employee_company.pay_cycle_day  # TODO: Make dynamic
# 	today = datetime.today()
# 	given_date = datetime.strptime(f"{company_audit_date}-{today.month}-{today.year}", "%d-%m-%Y").date()
# 	print(given_date,"given_date")
# 	start_date = given_date - relativedelta(months=1)
# 	print(start_date,"start_date")
# 	end_date = given_date
# 	print(end_date,"end_date")

# 	weekday_count = sum(1 for d in (start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)) if d.weekday() < 5)
# 	print(weekday_count,"weekday_count")
# 	holidays = holiday.objects.filter(holiday_date__range=[start_date, end_date])
# 	print(holidays,"holidays")
# 	working_days = weekday_count - holidays.count()
# 	leave_days = employees_attendance_info.objects.filter(date__range=[start_date, end_date], status='Absent').count()
# 	print(leave_days,"leave_days")

# 	lop_amount = (employee_salary.gross_salary / working_days) * leave_days
# 	print(lop_amount,"lop_amount")

# 	loan_deduction = LoanDeduction.objects.filter(employee=employee_instance, is_deleted=False, status='Accepted').first()
# 	loan_emi = 0
# 	if loan_deduction:
# 		if loan_deduction.fixed_amount:
# 			loan_emi = loan_deduction.fixed_amount
# 		elif loan_deduction.percentage_amount:
# 			loan_emi = (loan_deduction.percentage_amount / 100) * employee_salary.gross_salary

# 		print(f"Loan EMI to deduct from gross salary: {loan_emi}")

# 	total_deductions = employee_pf_deduction + employee_esi_deduction + lop_amount + loan_emi
# 	print(total_deductions,"total_deductions")

# 	# Net salary
# 	net_pay = total_earnings - total_deductions
# 	print(net_pay,"net_pay")

# 	# Final structured payslip
# 	payslip_data = {
# 		"employee name": employee_instance.first_name + " " + employee_instance.last_name,
# 		"employee id": employee_instance.employee_id,
# 		"employee_email": employee_instance.email,
# 		"earnings": {
# 			"basic pay": round(basic_pay, 2),
# 			"hra": round(hra, 2),
# 			"allowance": round(other_allowance, 2),
# 			"travel allowance": round(travel_allowance, 2) if travel_allowance else 0
# 		},
# 		"deductions": {
# 			"employee_pf": round(employee_pf_deduction, 2),
# 			"employee_esi": round(employee_esi_deduction, 2),
# 			"employer_pf": round(employee_company.employer_PF / 100 * basic_pay, 2),
# 			"employer_esi": round(employee_company.employer_ESI / 100 * employee_salary.gross_salary, 2),
# 			"loan_emi": round(loan_emi, 2),
# 			"lop": round(lop_amount, 2)
# 		},
# 		"net pay": round(net_pay, 2)
# 	}

# 	return JsonResponse([payslip_data], safe=False)


# @api_view(['GET'])
# def generate_all_payslips(request):

# 	active_employees = employee.objects.filter(is_active=True)
# 	print(active_employees, "active_employees")
# 	print("active_employees count", active_employees.count())
# 	all_payslips = []

# 	for emp in active_employees:
# 			employee_company = company_Settings.objects.get(company=emp.company_id.company_id)
# 			employee_salary = employee_salary_info.objects.get(employee_id=emp)
# 			print(employee_salary, "employee_salary")

# 			# CTC calculation
# 			ctc = employee_salary.gross_salary + employee_salary.variable_pay
# 			print(ctc, "ctc")

# 			# Initial earnings calculation
# 			basic_pay = ctc * (employee_company.basic_pay / 100)
# 			print(basic_pay, "basic_pay")
# 			hra = basic_pay * (employee_company.HRA / 100)
# 			print(hra, "hra")
# 			other_allowance = basic_pay * (employee_company.other_allowances / 100)
# 			print(other_allowance, "other_allowance")
# 			total_earnings = basic_pay + hra + other_allowance
# 			print(total_earnings, "total_earnings")
# 			travel_allowance = 0
# 			if total_earnings < ctc:
# 				travel_allowance = ctc - total_earnings
# 				total_earnings += travel_allowance
# 			print(travel_allowance, "travel_allowance")
# 			# Deductions
# 			employee_pf_deduction = (employee_company.employee_PF / 100) * basic_pay
# 			print(employee_pf_deduction, "employee_pf_deduction")
# 			employee_esi_deduction = (employee_company.employee_ESI / 100) * employee_salary.gross_salary
# 			print(employee_esi_deduction, "employee_esi_deduction")

# 			# Pay cycle date
# 			company_audit_day = employee_company.pay_cycle_day

# 			today = datetime.today()
# 			given_date = datetime.strptime(f"{company_audit_day}-{today.month}-{today.year}", "%d-%m-%Y").date()
# 			start_date = given_date - relativedelta(months=1)
# 			print(start_date, "start_date")
# 			end_date = given_date
# 			print(end_date, "end_date")

# 			# Working days calculation
# 			weekday_count = sum(
# 				1 for d in (start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1))
# 				if d.weekday() < 5
# 			)
# 			print(weekday_count, "weekday_count")
# 			holidays = holiday.objects.filter(holiday_date__range=[start_date, end_date])
# 			print(holidays, "holidays")
# 			working_days = weekday_count - holidays.count()
# 			print(working_days, "working_days")

# 			# LOP
# 			leave_days = employees_attendance_info.objects.filter(employee_id=emp.employee_id, date__range=[start_date, end_date], status='Absent').count()
# 			print(leave_days, "leave_days")
# 			lop_amount = (employee_salary.gross_salary / working_days) * leave_days if working_days > 0 else 0
# 			print(lop_amount, "lop_amount")

# 			# Loan deduction
# 			loan_deduction = LoanDeduction.objects.filter(employee_id=emp.employee_id, is_deleted=False, status='Accepted').first()

# 			loan_emi = 0
# 			if loan_deduction:
# 				if loan_deduction.fixed_amount:
# 					loan_emi = loan_deduction.fixed_amount
# 				elif loan_deduction.percentage_amount:
# 					loan_emi = (loan_deduction.percentage_amount / 100) * employee_salary.gross_salary
# 				print(f"Loan EMI to deduct from gross salary: {loan_emi}")

# 			total_deductions = employee_pf_deduction + employee_esi_deduction + lop_amount + loan_emi
# 			print(total_deductions, "total_deductions")
# 			net_pay = total_earnings - total_deductions
# 			print(net_pay, "net_pay")

# 			# Final structured payslip
# 			payslip_data = {
# 				"employee name": f"{emp.first_name} {emp.last_name}",
# 				"employee id": emp.employee_id,
# 				"employee_email": emp.email,
# 				"earnings": {
# 					"basic pay": round(basic_pay, 2),
# 					"hra": round(hra, 2),
# 					"allowance": round(other_allowance, 2),
# 					"travel allowance": round(travel_allowance, 2) if travel_allowance else 0
# 				},
# 				"deductions": {
# 					"employee_pf": round(employee_pf_deduction, 2),
# 					"employee_esi": round(employee_esi_deduction, 2),
# 					"employer_pf": round(employee_company.employer_PF / 100 * basic_pay, 2),
# 					"employer_esi": round(employee_company.employer_ESI / 100 * employee_salary.gross_salary, 2),
# 					"loan_emi": round(loan_emi, 2),
# 					"lop": round(lop_amount, 2)
# 				},
# 				"net pay": round(net_pay, 2)
# 			}
# 			all_payslips.append(payslip_data)
# 	return JsonResponse({"statuscode" : status.HTTP_200_OK, "status" : "success","data" : all_payslips}, status = status.HTTP_200_OK)

@api_view(['GET'])
def get_payslip(request, id):
	try:
		payslip = Payslip.objects.get(payslip_id=id)
	except Payslip.DoesNotExist:
		return JsonResponse({
			"statuscode": status.HTTP_404_NOT_FOUND,
			"status": "error",
			"message": "Payslip not found"
		}, status=status.HTTP_404_NOT_FOUND)

	data = {
		"employee_name": f"{payslip.employee.first_name} {payslip.employee.last_name}",
		"employee_id": payslip.employee.employee_id,
		"month": payslip.month,
		"year": payslip.year,
		"earnings": {
			"basic_pay": payslip.basic_pay,
			"hra": payslip.hra,
			"other_allowances": payslip.other_allowances,
			"travel_allowance": payslip.travel_allowance
		},
		"deductions": {
			"employee_pf": payslip.employee_pf,
			"employee_esi": payslip.employee_esi,
			"employer_pf": payslip.employer_pf,
			"employer_esi": payslip.employer_esi,
			"loan_emi": payslip.loan_emi,
			"lop": payslip.lop,
			"tax_deduction": payslip.tax_deduction
		},
		"net_pay": payslip.net_pay
	}

	return JsonResponse({
		"statuscode": status.HTTP_200_OK,
		"status": "success",
		"data": data
	}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_all_payslips(request):
	# Optional filters from query parameters
	employee_id = request.headers.get('employee-id')
	month = request.headers.get('month')
	year = request.headers.get('year')
	status_filter = request.headers.get('status')
 
	# Base queryset
	payslips = Payslip.objects.all()

	# Apply filters if provided
	if employee_id:
		payslips = payslips.filter(employee__employee_id=employee_id)
	if month:
		payslips = payslips.filter(month=month)
	if year:
		payslips = payslips.filter(year=year)
	if status_filter:
		payslips = payslips.filter(status=status_filter)

	# If no payslips found
	if not payslips.exists():
		return JsonResponse({
			"statuscode": status.HTTP_404_NOT_FOUND,
			"status": "error",
			"message": "No payslips found"
		}, status=status.HTTP_404_NOT_FOUND)

	# Structure response
	structured_data = []
	for payslip in payslips:
		structured_data.append({
			"employee_name": f"{payslip.employee.first_name} {payslip.employee.last_name}",
			"employee_id": payslip.employee.employee_id,
			"month": payslip.month,
			"year": payslip.year,
			"earnings": {
				"basic_pay": payslip.basic_pay,
				"hra": payslip.hra,
				"other_allowances": payslip.other_allowances,
				"travel_allowance": payslip.travel_allowance
			},
			"deductions": {
				"employee_pf": payslip.employee_pf,
				"employee_esi": payslip.employee_esi,
				"employer_pf": payslip.employer_pf,
				"employer_esi": payslip.employer_esi,
				"loan_emi": payslip.loan_emi,
				"lop": payslip.lop,
				"tax_deduction": payslip.tax_deduction
			},
			"net_pay": payslip.net_pay,
			"status": payslip.status
		})

	return JsonResponse({
		"statuscode": status.HTTP_200_OK,
		"status": "success",
		"data": structured_data
	}, status=status.HTTP_200_OK)

@api_view(['POST'])
def generate_all_payslips(request):
	active_employees = employee.objects.filter(is_active=True)
	payslip_objects = []
	response_data = []
	today = datetime.today()
	for emp in active_employees:
		try:
			employee_company = company_Settings.objects.get(company=emp.company_id.company_id)
			employee_salary = employee_salary_info.objects.get(employee_id=emp)
			# CTC and earnings
			annual_ctc = employee_salary.gross_salary + employee_salary.variable_pay
			if annual_ctc == 0:
				raise APIException(detail={"statuscode": 404, "status": "error", "message": "CTC not found."})
			monthly_ctc = annual_ctc / 12
			monthly_gross_salary = employee_salary.gross_salary / 12
			basic_pay = monthly_ctc * (employee_company.basic_pay / 100)
			hra = basic_pay * (employee_company.HRA / 100)
			other_allowance = basic_pay * (employee_company.other_allowances / 100)
			total_earnings = basic_pay + hra + other_allowance
			travel_allowance = max(monthly_ctc - total_earnings, 0)
			total_earnings += travel_allowance
			# Deductions
			employee_pf_deduction = (employee_company.employee_PF / 100) * basic_pay
			employee_esi_deduction = (employee_company.employee_ESI / 100) * monthly_gross_salary
			employer_pf = (employee_company.employer_PF / 100) * basic_pay
			employer_esi = (employee_company.employer_ESI / 100) * monthly_gross_salary
			# Pay cycle date
			company_audit_day = employee_company.pay_cycle_day
			given_date = datetime.strptime(f"{company_audit_day}-{today.month}-{today.year}", "%d-%m-%Y").date()
			start_date = given_date - relativedelta(months=1)
			end_date = given_date
			# Working days
			weekday_count = sum(
				1 for d in (start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1))
				if d.weekday() < 5
			)
			holidays_count = holiday.objects.filter(holiday_date__range=[start_date, end_date]).count()
			working_days = max(weekday_count - holidays_count, 0)
			# LOP
			leave_days = employees_attendance_info.objects.filter(
				employee_id=emp.employee_id, date__range=[start_date, end_date], status='Absent'
			).count()
			lop_amount = (monthly_gross_salary / working_days) * leave_days if working_days > 0 else 0
			# Loan
			loan_emi = 0
			loan = LoanDeduction.objects.filter(employee_id=emp.employee_id, is_deleted=False, status='Accepted').first()
			if loan:
				if loan.fixed_amount:
					loan_emi = loan.fixed_amount
				elif loan.percentage_amount:
					loan_emi = (loan.percentage_amount / 100) * monthly_gross_salary
				elif loan.tenure:
					try:
						loan_emi = loan.loan_amount / loan.tenure
					except ZeroDivisionError:
						loan_emi = 0
			# Tax deduction
			monthly_tax_deduction = 0
			monthly_tax_deduction = calculate_employee_tax_deduction(emp.employee_id, annual_ctc)
			print(monthly_tax_deduction, "monthly_tax_deduction")
			# Final amounts
			total_deductions = employee_pf_deduction + employee_esi_deduction + lop_amount + loan_emi + monthly_tax_deduction
			net_pay = total_earnings - total_deductions
			# Avoid duplicates
			month_name = given_date.strftime('%B')
			year = given_date.year
			if Payslip.objects.filter(employee=emp, month=month_name, year=year).exists():
				continue
			# Create Payslip instance
			payslip = Payslip(
				employee=emp,
				month=month_name,
				year=year,
				basic_pay=round(basic_pay, 2),
				hra=round(hra, 2),
				other_allowances=round(other_allowance, 2),
				travel_allowance=round(travel_allowance, 2),
				employee_pf=round(employee_pf_deduction, 2),
				employee_esi=round(employee_esi_deduction, 2),
				employer_pf=round(employer_pf, 2),
				employer_esi=round(employer_esi, 2),
				loan_emi=round(loan_emi, 2),
				lop=round(lop_amount, 2),
				tax_deduction=round(monthly_tax_deduction, 2),
				net_pay=round(net_pay, 2),
				status="pending",
				updated_by=request.user.id if request.user.is_authenticated else None
			)
			payslip_objects.append(payslip)
			# Add to response preview
			response_data.append({
				"employee_name": f"{emp.first_name} {emp.last_name}",
				"employee_id": emp.employee_id,
				"month": month_name,
				"year": year,
				"net_pay": round(net_pay, 2)
			})
		except Exception as e:
			raise APIException(detail={"statuscode": 500, "status": "error", "message": f"Error for {emp.employee_id}: {str(e)}"})
	# Perform bulk insert
	if payslip_objects:
		Payslip.objects.bulk_create(payslip_objects)
	return JsonResponse({
		"statuscode": status.HTTP_200_OK,
		"status": "success",
		"inserted_count": len(payslip_objects),
		"data": response_data
	}, status=status.HTTP_200_OK)


@api_view(['PATCH'])
def update_payslip_status(request, id):
	try:
		payslip = Payslip.objects.get(payslip_id=id)
	except Payslip.DoesNotExist:
		return JsonResponse({"statuscode": status.HTTP_404_NOT_FOUND, "status": "error", "message": "Payslip not found"}, status=status.HTTP_404_NOT_FOUND)
	serializer = PayslipStatusUpdateSerializer(payslip, data=request.data, partial=True)
	if serializer.is_valid():
		datas = serializer.validated_data
		datas['status'] = string.capwords(datas['status'])
		if datas['status'] == "Finalized":
			Payslip.objects.filter(payslip_id=id).update(status=datas['status'], updated_by=request.user.id if request.user.is_authenticated else None)
			return Response({"statuscode" : status.HTTP_201_CREATED, "status" : "success", "message" : "Payslip finalized successfully "}, status = status.HTTP_201_CREATED) 
	return Response({"message" : serializer.errors, "status" : "error"}, status = status.HTTP_400_BAD_REQUEST)