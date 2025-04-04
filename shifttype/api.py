from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import shift_type
from .serializers import shift_type_serializer, Shift_type_list_serializer



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def shift_type_create(request):
    serializer_data = shift_type_serializer(data = request.data)
    if serializer_data.is_valid():
        serializer_data.save()
        return Response({"statuscode":status.HTTP_201_CREATED, "status":"success", "message":"created successfully", "data":'serializer.data'}, status=status.HTTP_201_CREATED)
    return Response(serializer_data.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def shift_type_list(request):
    listOfShift = shift_type.objects.all()
    serialized_data = Shift_type_list_serializer(instance = listOfShift, many = True)
    return Response({"statuscode":status.HTTP_200_OK, "status":"success", "data":serialized_data.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def shift_type_view(request, id):
    try:
        instance = shift_type.objects.get(shift_type_id = id)
    except shift_type.DoesNotExist:
        return Response({"detail": "shift_type not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serialized_data = shift_type_serializer(instance = instance)
    return Response({"statuscode":status.HTTP_200_OK, "status":"success", "data":serialized_data.data}, status=status.HTTP_200_OK)
    

@api_view(['PATCH'])
@permission_classes((IsAuthenticated,))
def shift_type_update(request, id):
    try:
        instance = shift_type.objects.get(shift_type_id = id)
    except shift_type.DoesNotExist:
        return Response({"detail":"shift_type not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serialized_data = shift_type_serializer(instance, data= request.data, partial = True)
    if serialized_data.is_valid():
        serialized_data.save()
        return Response({"statuscode":status.HTTP_200_OK, "status":"success", "data":serialized_data.data}, status=status.HTTP_200_OK)
    return Response(serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def shift_type_delete(request, id):
    try:
        shift_type.objects.get(shift_type_id = id)
    except shift_type.DoesNotExist:
        return Response({"detail":"shift_type not found"}, status=status.HTTP_404_NOT_FOUND)
    shift_type.objects.filter(shift_type_id = id).update(is_active = False)
    return Response({"statuscode":status.HTTP_200_OK,"status":"success"}, status=status.HTTP_200_OK)
    

