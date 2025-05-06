import openpyxl
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from rest_framework.decorators import api_view
import base64
import io
from .models import holiday
import pandas as pd


@api_view(['POST'])
def index(request):    
    try:
        decoded_file = base64.b64decode(request.body)
        excel_file = io.BytesIO(decoded_file)
        wb = openpyxl.load_workbook(excel_file) #io.BytesIO: Creates an in-memory file-like object.
        
        worksheet = wb[wb.sheetnames[0]]
        data = worksheet.values
        columns = next(data)  # First row as column names
        
        df = pd.DataFrame(data, columns=columns)
        df.columns = [col.strip().lower() for col in df.columns]
        required_columns = ['holiday date', 'occasion', 'leave type']
        for col in required_columns:
                if col not in df.columns:
                        return Response({"status": "error", "message": f"Missing required column: {col}"}, status=400)
                    
        df = df.rename(columns={
        'holiday date': 'holiday_date',
        'occasion': 'occasion',
        'leave type': 'leave_type'
        })
        converted_date=[]
        for index,date_value in df['holiday_date'].items():
            try:
                converted_date.append(pd.to_datetime(date_value, errors='raise'))
            except ValueError:
                return Response({"status": "error", "message": f"Invalid date format in at row : {index +2}, value : {date_value}"}, status=400)
        df['holiday_date'] = converted_date
        df = df.dropna(subset=['holiday_date'])
        df = df.sort_values(by='holiday_date')

        created, updated = [], []
        for _, row in df.iterrows():
                date = row['holiday_date'].date()
                occasion = str(row['occasion']).strip()
                leave_type = str(row['leave_type']).strip()
                #, is_created
                holiday_obj, is_created = holiday.objects.update_or_create(
                        holiday_date=date,
                        defaults={
                                'occasion': occasion,
                                'leave_type': leave_type
                        }
                )
                
                entry = {
                "holiday_date": str(date),
                "occasion": occasion,
                "leave_type": leave_type
                }
                if is_created:
                    created.append(entry)
                else:
                    updated.append(entry)

        return Response({"statuscode": 200,"status": "success","created": created,"updated": updated}, status=200)
        
    except Exception as e:
        error_message = (
            type(e).__name__,          # TypeError
            __file__,                  # /tmp/example.py
            e.__traceback__.tb_lineno,  # line number
            str(e)
        )
        return Response({"status": "error", "message": error_message}, status=500)

@api_view(['POST'])
def create_holiday(request):
    try:
        serializer = HolidayCreateSerializer(data = request.data)
        if serializer.is_valid():
            data = serializer.validated_data            
            holiday.objects.create(**data)
            return Response({"statuscode":status.HTTP_201_CREATED,"status":"success",'message':f'{serializer.data['occasion']} Holiday stored'},status=status.HTTP_201_CREATED)
        
    except Exception as e:
        error_message = (
            type(e).__name__,          # TypeError
            __file__,                  # /tmp/example.py
            e.__traceback__.tb_lineno,  # line number
            str(e)
        )
        return Response({"status":"error","message" : error_message}, status = 500)
    return Response({"status":"error","message":serializer.errors}, status = 400)

@api_view(['PATCH'])
def update_holiday(request,id):
    try:
        holiday_obj = holiday.objects.get(holiday_id = id)
    except holiday.DoesNotExist:
        return Response({"status": "error", "message": "Holiday not found"}, status=404)
    
    serializer = HolidayUpdateSerializer(holiday_obj,data = request.data, partial = True)
    
    if serializer.is_valid():
        print('inside serializer')
        holiday.objects.filter(holiday_id = id).update(**serializer.validated_data)        
        print(serializer)
        return Response({"statuscode":status.HTTP_200_OK,"status": "success", "message": "Holiday updated successfully","data" : serializer.data}, status=200)
    return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])    
def delete_holiday(request, id):
    try:
        holiday_obj = holiday.objects.get(holiday_id=id)
        holiday_obj.delete()
        return Response({"status": "success", "message": "Holiday deleted successfully"}, status=200)
    except holiday.DoesNotExist:
        return Response({"status": "error", "message": "Holiday not found"}, status=404)
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)