from django.shortcuts import render, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from loan_deduction.serializers import CreateloanSerializer, LoanSerializer, RepaymentSerializer, UpdateloanSerializer   
from .models import LoanDeduction, Repayment
# Create your views here.

from django.shortcuts import render

def loan_list(request):
    if request.method =='GET':
        loans = LoanDeduction.objects.all()
        print("loans",loans)
        return render(request, 'loan_list.html',{'loans':loans})
    
    if request.method == 'POST':
        loan_type = request.POST.get('loan_type')
        loan_amount = request.POST.get('loan_amount')   
        reasons = request.POST.get('reasons')
        repayment_period = request.POST.get('repayment_period')
        monthly_emi = request.POST.get('monthly_emi')
        LoanDeduction.objects.create(loan_type = loan_type, loan_amount = loan_amount, reasons = reasons, repayment_period = repayment_period, monthly_emi = monthly_emi)
        return render(request, 'loan_list.html')
    
def loan_details(request,pk):
    if request.method == 'GET':
        loan = LoanDeduction.objects.get(loan_id = pk)
        return render(request, 'loan_details.html',{'loan':loan})
    
    if request.method == 'PUT':
        loan = LoanDeduction.objects.get(loan_id = pk)
        loan_type = request.POST.get('loan_type')
        loan_amount = request.POST.get('loan_amount')   
        reasons = request.POST.get('reasons')
        repayment_period = request.POST.get('repayment_period')
        monthly_emi = request.POST.get('monthly_emi')
        LoanDeduction.objects.filter(loan_id = pk).update(loan_type = loan_type, loan_amount = loan_amount, reasons = reasons, repayment_period = repayment_period, monthly_emi = monthly_emi)
        return render(request, 'loan_details.html')
    
    if request.method == 'DELETE':
        LoanDeduction.objects.filter(loan_id = pk).update(is_deleted = True)
        return HttpResponse("Loan deleted successfully")


# class LoanList(APIView):
#     def get(self,request):
#         loans = LoanDeduction.objects.all()
#         serializer = LoanSerializer(loans, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
    

# class LoanCreate(APIView):
#     def post(self,request):
#         serializer = CreateloanSerializer(data = request.data)
#         if serializer.is_valid():
#             LoanDeduction.objects.create(**serializer.validated_data)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
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
#         return Response(serializer.data, status=status.HTTP_200_OK) 
        
#     def put(self,request,pk):
#          loan = self.get_object(pk)
#          serializer = UpdateloanSerializer(loan, data = request.data)
#          if serializer.is_valid():
#             LoanDeduction.objects.filter(loan_id =pk).update(**serializer.validated_data)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#          return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self,request,pk):
#         loan = self.get_object(pk)    
#         LoanDeduction.objects.filter(loan_id = pk).update(is_deleted = True)
#         return Response({"details":"Loan deleted successfully"},status=status.HTTP_204_NO_CONTENT)    
    
    

        
    