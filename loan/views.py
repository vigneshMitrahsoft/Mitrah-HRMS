from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, HttpResponse
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from loan.serializers import CreateloanSerializer, LoanSerializer, RepaymentSerializer, UpdateloanSerializer   
from .models import LoanDeduction, Repayment
from datetime import datetime
# Create your views here.

from django.shortcuts import render

def loan_list(request):
    if request.method =='GET':
        loans = LoanDeduction.objects.all().filter(is_deleted = False)
        # print("loans",loans)
        return render(request, 'loan_list.html',{'loans':loans})
    
def loan_create(request):
    if request.method == 'POST':
        loan_type = request.POST.get('loan_type')
        loan_amount = request.POST.get('loan_amount')   
        reasons = request.POST.get('reasons')
        repayment_type = request.POST.get('repayment_type')
        percentage_amount = request.POST.get('percentage_amount')   
        fixed_amount = request.POST.get('fixed_amount')
        LoanDeduction.objects.create(loan_type = loan_type, loan_amount = loan_amount, reasons = reasons, requested_date=datetime.now(), repayment_type = repayment_type, percentage_amount= percentage_amount, fixed_amount = fixed_amount, created_at = datetime.now())
        return redirect('loan_list_template')
    return render(request, 'loan_create.html')
    
def loan_detail(request,pk):
    if request.method == 'GET':
        loan = LoanDeduction.objects.get(loan_id = pk)
        return render(request, 'loan_details.html',{'loan':loan})

def loan_update(request,pk):
    loan = LoanDeduction.objects.get(loan_id = pk)
    if request.method == 'POST':
        loan_type = request.POST.get('loan_type')
        loan_amount = request.POST.get('loan_amount')   
        reasons = request.POST.get('reasons')
        repayment_type = request.POST.get('repayment_type')
        percentage_amount = request.POST.get('percentage_amount')
        fixed_amount = request.POST.get('fixed_amount')
        LoanDeduction.objects.filter(loan_id = pk).update(loan_type = loan_type, loan_amount = loan_amount, reasons = reasons, repayment_type = repayment_type,percentage_amount = percentage_amount, fixed_amount = fixed_amount)
        return HttpResponseRedirect(reverse('loan_list_template')) 
    return render(request, 'loan_update.html',{'loan': loan})
    
def loan_delete(request,pk):
    # if request.method == 'POST':
        LoanDeduction.objects.filter(loan_id = pk).update(is_deleted = True)
        return HttpResponseRedirect(reverse('loan_list_template'))

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
    
    

        
    