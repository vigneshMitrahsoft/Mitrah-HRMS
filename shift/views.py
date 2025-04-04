# from django.shortcuts import render
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status
# from .models import *
# from .serializers import  shiftSerializer, ShiftListSerializer, employeeListSerializer
# Create your views here.


# @api_view(['POST'])
# # @permission_classes((IsAuthenticated,))
# def shift_type_create(request):
#     serializer_data = shiftTypeSerializer(data = request.data)
#     if serializer_data.is_valid():
#         serializer_data.save()
#         return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"created successfully","data":'serializer.data'},status=status.HTTP_201_CREATED)
#     return Response(serializer_data.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# # @permission_classes((IsAuthenticated,))
# def shift_type_list(request):
#     listOfShift = shift_type.objects.all()
#     serialized_data = ShiftTypeListSerializer(instance = listOfShift, many = True)
#     return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)


# @api_view(['GET', 'PATCH', 'DELETE'])
# # @permission_classes((IsAuthenticated,))
# def shift_type_view(request, ID):
#     try:
#         instance = shift_type.objects.get(shift_type_id = ID)
#     except shift_type.DoesNotExist:
#         return Response({"detail": "shift_type not found"}, status=status.HTTP_404_NOT_FOUND)
    
#     if request.method == 'GET':
#         serialized_data = shiftTypeSerializer(instance = instance)
#         return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)
    
#     if request.method == 'PATCH':
#         serialized_data = shiftTypeSerializer(instance, data= request.data, partial = True)
#         if serialized_data.is_valid():
#             serialized_data.save()
#             return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)
#         return Response(serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)

#     if request.method == 'DELETE':
#         shift_type.objects.filter(shift_id = ID).update(is_active = False)
#         return Response({"statuscode":status.HTTP_200_OK,"status":"success"},status=status.HTTP_200_OK)



# @api_view(['POST'])
# # @permission_classes((IsAuthenticated,))
# def shift_create(request):
#     # print('helo')
#     # request['user'] = 1 
#     serializer_data = shiftSerializer(data = request.data, context={"request": request})
#     if serializer_data.is_valid():
#         serializer_data.save()
#         return Response({"statuscode":status.HTTP_201_CREATED,"status":"success","message":"created successfully","data":'serializer.data'},status=status.HTTP_201_CREATED)
#     return Response(serializer_data.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# # @permission_classes((IsAuthenticated,))
# def shift_list(request):
#     listOfShift = shift.objects.all()
#     serialized_data = ShiftListSerializer(instance = listOfShift, many = True)
#     return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)

# @api_view(['GET', 'PATCH', 'DELETE'])
# # @permission_classes((IsAuthenticated,))
# def shift_view(request, ID):
#     try:
#         instance = shift.objects.get(shift_id = ID)
#     except shift.DoesNotExist:
#         return Response({"detail":"shift not found"},status=status.HTTP_400_BAD_REQUEST)
    
#     if request.method == 'GET':
#         serialized_data = ShiftListSerializer(instance = instance)
#         return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)
    
#     if request.method == 'PATCH':
#         serialized_data = shiftSerializer(instance, data= request.data, partial = True)
#         if serialized_data.is_valid():
#             serialized_data.save()
#             return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)
#         return Response(serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)

#     if request.method == 'DELETE':
#         shift.objects.filter(shift_id = ID).update(is_active = False)
#         return Response({"statuscode":status.HTTP_200_OK,"status":"success"},status=status.HTTP_200_OK)


# @api_view(['GET'])
# # @permission_classes((IsAuthenticated,))
# def emp_shift_list(request):
#     listOfShift = employee_shift.objects.all()
#     serialized_data = employeeListSerializer(instance = listOfShift, many = True)
#     return Response({"statuscode":status.HTTP_200_OK,"status":"success","data":serialized_data.data},status=status.HTTP_200_OK)