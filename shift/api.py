from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import shift
from .serializers import  shift_serializer, shiftlist_serializer

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def shift_create(request):
    serializer_data = shift_serializer(data = request.data, context={"request": request})
    if serializer_data.is_valid():
        serializer_data.save()
        return Response({"statuscode":status.HTTP_201_CREATED, "status":"success", "message":"created successfully", "data":'serializer.data'}, status=status.HTTP_201_CREATED)
    return Response(serializer_data.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def shift_list(request):
    listOfShift = shift.objects.all()
    serialized_data = shiftlist_serializer(instance = listOfShift, many = True)
    return Response({"statuscode":status.HTTP_200_OK, "status":"success", "data":serialized_data.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def shift_view(request, id):
    try:
        instance = shift.objects.get(shift_id = id)
    except shift.DoesNotExist:
        return Response({"detail":"shift not found"}, status=status.HTTP_400_BAD_REQUEST)

    serialized_data = shiftlist_serializer(instance = instance)
    return Response({"statuscode":status.HTTP_200_OK, "status":"success", "data":serialized_data.data}, status=status.HTTP_200_OK)
    
@api_view(['PATCH'])
@permission_classes((IsAuthenticated,))
def shift_update(request, id):
    try:
        instance = shift.objects.get(shift_id = id)
    except shift.DoesNotExist:
        return Response({"detail":"shift not found"}, status=status.HTTP_400_BAD_REQUEST)
    serialized_data = shift_serializer(instance, data = request.data, partial = True)
    if serialized_data.is_valid():
        serialized_data.save()
        return Response({"statuscode":status.HTTP_200_OK, "status":"success","data":serialized_data.data}, status=status.HTTP_200_OK)
    return Response(serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def shift_delete(request, id):
    try:
        shift.objects.get(shift_id = id)
    except shift.DoesNotExist:
        return Response({"detail":"shift not found"},status=status.HTTP_400_BAD_REQUEST)
    
    shift.objects.filter(shift_id = id).update(is_active = False)
    return Response({"statuscode":status.HTTP_200_OK, "status":"success"}, status=status.HTTP_200_OK)