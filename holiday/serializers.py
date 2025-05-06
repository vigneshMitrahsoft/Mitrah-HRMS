from .models import holiday
from rest_framework import serializers
 
class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = holiday
        fields = '__all__'
        read_only_fields = ['holiday_id', 'created_at', 'updated_at']
    
class HolidayCreateSerializer(serializers.Serializer):
    occasion = serializers.CharField(required=True)
    leave_type = serializers.CharField(required=True)
    holiday_date = serializers.DateField(required=True)

    def validate(self,data):
        if holiday.objects.filter(holiday_date = data['holiday_date']).exists():
            raise serializers.ValidationError("Holiday date already exists")
        return data

class HolidayUpdateSerializer(serializers.Serializer):
    holiday_id = serializers.IntegerField(required=True)
    occasion = serializers.CharField(required=True)
    leave_type = serializers.CharField(required=True)
    holiday_date = serializers.DateField(required=True)

    # def validate(self, data):
    #     if 'holiday_date' in data:
    #         if not isinstance(data['holiday_date'], str):
    #             raise serializers.ValidationError("Holiday date must be a string")
    #     return data

