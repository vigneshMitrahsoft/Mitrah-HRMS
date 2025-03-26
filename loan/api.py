from datetime import datetime, timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import LoanDeduction, Repayment
from .serializers import LoanSerializer, CreateloanSerializer, UpdateloanSerializer


class LoanList(APIView):
    def get(self,request):
        loans = LoanDeduction.objects.all()
        serializer = LoanSerializer(loans, many=True)
        return Response({"statuscode": status.HTTP_200_OK,"status":"success","data":serializer.data},status=status.HTTP_200_OK) 
    

    def post(self,request):
        serializer = CreateloanSerializer(data = request.data)
        if serializer.is_valid():
            LoanDeduction.objects.create(**serializer.validated_data)
            return Response({"statuscode": status.HTTP_201_CREATED,"status":"success","data":serializer.data},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoanDetails(APIView):
    def get_object(self,pk):
        try:
            return LoanDeduction.objects.get(loan_id = pk)
        except LoanDeduction.DoesNotExist:
            return Response({"details":"loan not found"},status=status.HTTP_404_NOT_FOUND)

    def get(self,request,pk):
        loan = self.get_object(pk)
        serializer = LoanSerializer(loan)
        return Response({"statuscode": status.HTTP_200_OK,"status":"success","data":serializer.data},status=status.HTTP_200_OK) 
        
    def patch(self, request, pk):
        loan = self.get_object(pk)
        data = request.data
        serializer = UpdateloanSerializer(loan, data=data, partial=True)  
        if serializer.is_valid():
            LoanDeduction.objects.filter(loan_id=pk).update(**serializer.validated_data, updated_at=datetime.now())   
            return Response({"statuscode": status.HTTP_200_OK,"status":"success","data":serializer.validated_data},status=status.HTTP_200_OK) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk):
        loan = self.get_object(pk)    
        LoanDeduction.objects.filter(loan_id = pk).update(is_deleted = True)
        return Response({"details":"Loan deleted successfully"},status=status.HTTP_204_NO_CONTENT)    