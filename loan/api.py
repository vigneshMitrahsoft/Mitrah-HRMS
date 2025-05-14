import calendar
from datetime import datetime, timedelta, date
from django.db import transaction
from django.utils import timezone
import string
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import LoanDeduction, Repayment, EmiRepayments
from .serializers import *
from employee.models import employee
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from auth.views import IsAuthorized
from employee.models import employee_salary_info
from company.models import company_Settings
from dateutil.relativedelta import relativedelta

# class LoanList(APIView):
#     def get(self,request):
#         loans = LoanDeduction.objects.all()
#         serializer = LoanSerializer(loans, many=True)
#         return Response({"statuscode": status.HTTP_200_OK,"status":"success","data":serializer.data},status=status.HTTP_200_OK) 
	

#     def post(self,request):
#         serializer = CreateloanSerializer(data = request.data)
#         if serializer.is_valid():
#             LoanDeduction.objects.create(**serializer.validated_data)
#             return Response({"statuscode": status.HTTP_201_CREATED,"status":"success","data":serializer.validated_data},status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class LoanDetails(APIView):
#     def get_object(self,pk):
#         try:
#             return LoanDeduction.objects.get(loan_id = pk)
#         except LoanDeduction.DoesNotExist:
#             return Response({"details":"loan not found"},status=status.HTTP_404_NOT_FOUND)

#     def get(self,request,pk):
#         loan = self.get_object(pk)
#         serializer = LoanSerializer(loan)
#         return Response({"statuscode": status.HTTP_200_OK,"status":"success","data":serializer.data},status=status.HTTP_200_OK) 
		
#     def patch(self, request, pk):
#         loan = self.get_object(pk)
#         data = request.data
#         serializer = UpdateloanSerializer(loan, data=data, partial=True)  
#         if serializer.is_valid():
#             LoanDeduction.objects.filter(loan_id=pk).update(**serializer.validated_data, updated_at=datetime.now())   
#             return Response({"statuscode": status.HTTP_200_OK,"status":"success","data":serializer.validated_data},status=status.HTTP_200_OK) 
#         return Response({"message":serializer.errors,"status":"error"},status=status.HTTP_400_BAD_REQUEST)

#     def delete(self,request,pk):
#         loan = self.get_object(pk)    
#         LoanDeduction.objects.filter(loan_id = pk).update(is_deleted = True)
#         return Response({"details":"Loan deleted successfully"},status=status.HTTP_204_NO_CONTENT)    
def check_loan_exist(pk):
	try:
		loan = LoanDeduction.objects.get(loan_id = pk)
	except LoanDeduction.DoesNotExist:
		raise APIException(detail={"statuscode": 404, "status": "error", "message": "Loan not found"})
		# return None
	return loan

# #TODO: function fro creating the repayments 
# def create_repayment_records(pk):
#     print("inside the repayment creation")

#     loan = check_loan_exist(pk)

#     loan_amount = loan.loan_amount
#     repayment_type = loan.repayment_type.strip().lower()
#     remaining_balance = loan.loan_amount
#     repayments_records =[]


#     if repayment_type == 'monthly':
#         payment_date = datetime.now()

#         if loan.percentage_amount:
#             monthly_payment = loan_amount * (loan.percentage_amount/100)
#         if loan.fixed_amount:
#             monthly_payment = loan.fixed_amount

#         while remaining_balance > 0:
#             if remaining_balance < monthly_payment:
#                 monthly_payment = remaining_balance

#             repayment = Repayment(loan_id = loan, payment_date = payment_date, amount_paid = monthly_payment, remaining_balance = remaining_balance - monthly_payment)
#             repayments_records.append(repayment)
#             remaining_balance -= monthly_payment
#             payment_date += timedelta(days=30)

#     print("Repayments to be created:", repayments_records)

# # Attempt bulk create
#     try:
#         repayment = Repayment.objects.bulk_create(repayments_records)
#         print(f"Successfully created {len(repayment)} repayment records.")
#     except Exception as e:
#         print("Error creating repayment records:", e)
    
#     return repayment

def create_repayment_records(pk):
    try:
        loan = LoanDeduction.objects.get(pk=pk, is_deleted=False)
    except LoanDeduction.DoesNotExist:
        raise APIException(detail={"statuscode": 404, "status": "error", "message": "Loan not found."})

    employee = loan.employee
    approved_date = loan.approved_date
    repayment_type = loan.repayment_type
    loan_amount = loan.loan_amount
    percentage_amount = loan.percentage_amount
    fixed_amount = loan.fixed_amount
    tenure = loan.tenure
    remaining_balance = loan_amount

    # Get employee gross salary
    try:
        salary_info = employee_salary_info.objects.get(employee_id=employee.employee_id)
        gross_salary = salary_info.gross_salary
    except employee_salary_info.DoesNotExist:
        raise APIException(detail={"statuscode": 404, "status": "error", "message": "Gross salary not found."})

    # Get company pay cycle day
    try:
        company_setting = company_Settings.objects.get(company_id=employee.company_id)
        pay_cycle_day = company_setting.pay_cycle_day or 1
    except company_Settings.DoesNotExist:
        raise APIException(detail={"statuscode": 404, "status": "error", "message": "Company settings not found."})

    # Determine EMI amount
    if repayment_type == 'percentage':
        if not percentage_amount:
            raise APIException(detail={"statuscode": 400, "status": "error", "message": "Percentage EMI missing."})
        emi_amount = round((gross_salary * percentage_amount) / 100, 2)
    elif repayment_type == 'fixed':
        if not fixed_amount:
            raise APIException(detail={"statuscode": 400, "status": "error", "message": "Fixed EMI amount missing."})
        emi_amount = fixed_amount
    elif repayment_type == 'tenure':
        if not tenure:
            raise APIException(detail={"statuscode": 400, "status": "error", "message": "Tenure EMI missing."})
        emi_amount = round(loan_amount / tenure, 2)
        if emi_amount > gross_salary:
            raise APIException(detail={"statuscode": 400, "status": "error", "message": "EMI amount > gross salary."})
    else:
        raise APIException(detail={"statuscode": 400, "status": "error", "message": "Invalid repayment type."})

    if emi_amount <= 0:
        raise APIException(detail={"statuscode": 400, "status": "error", "message": "EMI must be > 0."})

    # Loop to generate EMIRepayment records
    payment_date = approved_date
    current_date = timezone.now().date()
    emi_repayments = []
    actual_repayments = []

    while remaining_balance > 0:
        # Set payment day of the month
        year = payment_date.year
        month = payment_date.month

        last_day = calendar.monthrange(year, month)[1]
        day = min(pay_cycle_day, last_day)

        due_date = timezone.datetime(year, month, day).date()

        # Amount paid logic
        payment = emi_amount if remaining_balance >= emi_amount else remaining_balance

        # Determine EMI status
        if due_date.day == current_date.day and due_date.month == current_date.month and due_date.year == current_date.year:
            status = "Paid"
            actual_repayments.append(
                Repayment(
                    loan=loan,
                    payment_date=due_date,
                    amount_paid=payment,
                    remaining_balance=remaining_balance - payment
                )
            )
        else:
            status = "Upcoming"

        emi_repayments.append(
            EmiRepayments(
                loan=loan,
                payment_date=due_date,
                amount=payment,
                status=status,
                remaining_balance=remaining_balance - payment
            )
        )

        remaining_balance -= payment
        payment_date += relativedelta(months=1)

    # Save EMI schedule and current month's repayment
    try:
        EmiRepayments.objects.bulk_create(emi_repayments)
        if actual_repayments:
            Repayment.objects.bulk_create(actual_repayments)
    except Exception as e:
        raise APIException(detail={"statuscode": 500, "status": "error", "message": "Failed to save EMI or repayments."})

    return {"emi_repayments_created": len(emi_repayments), "repayment_created": len(actual_repayments)}

@api_view(('GET',))
@permission_classes((IsAuthenticated,))
@IsAuthorized(['hr'])
def loan_list(request):
	loan = LoanDeduction.objects.all()
	serializer = loanSerializer(loan, many = True)
	return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "data" : serializer.data}, status = status.HTTP_200_OK)

@api_view(('POST',))
@permission_classes((IsAuthenticated,))
def loan_create(request):
	employee_id = request.user.employee_id
	# employee_id = employee.objects.get(employee_id = 1)
	serializer = createLoanSerializer(data = request.data)
	if serializer.is_valid():
		LoanDeduction.objects.create(**serializer.validated_data, employee_id = employee_id)
		return Response({"statuscode" : status.HTTP_201_CREATED, "status" : "success", "message" : "Loan created successfully"}, status = status.HTTP_201_CREATED)
	return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

@api_view(('GET',))
def loan_detail_by_employee(request, pk):
	loan = check_loan_exist(pk)
	serializer = loanSerializer(loan)
	return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "data" : serializer.data}, status = status.HTTP_200_OK)


@api_view(('PATCH',))
def update_loan(request, pk):
	loan = check_loan_exist(pk)
	serializer = updateLoanSerializer(loan, data = request.data, partial = True)  
	if serializer.is_valid():
		LoanDeduction.objects.filter(loan_id = pk).update(**serializer.validated_data, updated_at = datetime.now())   
		return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "message" : "Loan updated successfully"}, status = status.HTTP_200_OK) 
	return Response({"message" : serializer.errors,"status" : "error"}, status = status.HTTP_400_BAD_REQUEST)

@api_view(('DELETE',))
def loan_delete(request, pk):
	loan = check_loan_exist(pk)
	LoanDeduction.objects.filter(loan_id = pk).update(is_deleted = True)
	return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "message" : "Loan deleted successfully"}, status = status.HTTP_204_NO_CONTENT)

@api_view(('PATCH',))
def request_acceptance(request, pk):
	loan = check_loan_exist(pk)
	serializer = loanStatusUpdateSerializer(loan, data = request.data, partial = True)
	if serializer.is_valid():
		data = serializer.validated_data

		data['status'] = string.capwords(data['status'])

		if data['status'] not in ['Accepted', 'Rejected']:
			raise ValidationError(detail = {"statuscode" : status.HTTP_400_BAD_REQUEST, "status" : "error", "message" : "Invaild status"})
		
		if data['status'] == 'Accepted':
			LoanDeduction.objects.filter(loan_id = pk).update(status = "Accepted", start_date = datetime.now(), updated_at = datetime.now(), approved_date = datetime.now()) 
			print("Calling create_repayment_records function...")  
			create_repayment_records(pk) 
			print("create_repayment_records function executed.")
			return Response({"statuscode" : status.HTTP_201_CREATED, "status" : "success", "message" : "Loan accepted successfully and created repayment"}, status = status.HTTP_201_CREATED)
		
		if data['status'] == 'Rejected':
			LoanDeduction.objects.filter(loan_id = pk).update(status = "Rejected", updated_at = datetime.now())
			return  Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "message" : "Loan rejected successfully"}, status = status.HTTP_200_OK)
		
		if data['status'] == "Completed":
			LoanDeduction.objects.filter(loan_id = pk).update(status = "Completed", updated_at = datetime.now())
			return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "message" : "Loan completed successfully"}, status = status.HTTP_200_OK)

	return Response({"message" : serializer.errors, "status" : "error"}, status = status.HTTP_400_BAD_REQUEST)

@api_view(('GET',))
@permission_classes((IsAuthenticated,))
def repayment_list(request):
	repayment = Repayment.objects.all()
	serializer = repaymentSerializer(repayment, many = True)
	return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "data" : serializer.data}, status = status.HTTP_200_OK)

@api_view(('GET',))
@permission_classes((IsAuthenticated,))
def repayment_detail(request, pk):
	repayment = Repayment.objects.filter(loan_id = pk)
	serializer = repaymentSerializer(repayment, many = True)
	return Response({"statuscode" : status.HTTP_200_OK, "status" : "success", "data" : serializer.data}, status = status.HTTP_200_OK)

#TODO: need to implement the creation of repayments     
@api_view(('POST',))
@permission_classes((IsAuthenticated,))
def repayment_create(request, pk):
	loan = check_loan_exist(pk)
	serializer = repaymentCreateSerializer(data = request.data)
	if serializer.is_valid():
		Repayment.objects.create(**serializer.validated_data, loan_id = loan.loan_id)
		return Response({"statuscode" : status.HTTP_201_CREATED, "status" : "success" , "message" : "Repayment created successfully"}, status = status.HTTP_201_CREATED)
	return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)



