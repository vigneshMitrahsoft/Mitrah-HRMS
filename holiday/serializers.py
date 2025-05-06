from .models import holiday
from rest_framework import serializers
 
class holidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = holiday
        fields = '__all__'
        read_only_fields = ['holiday_id', 'created_at', 'updated_at']
    
class holidayCreateSerializer(serializers.Serializer):
    occasion = serializers.CharField(required = True)
    leave_type = serializers.CharField(required = True)
    holiday_date = serializers.DateField(required = True)

    def validate(self,data):
        if holiday.objects.filter(holiday_date = data['holiday_date']).exists():
            raise serializers.ValidationError("Holiday date already exists")
        return data

class holidayUpdateSerializer(serializers.Serializer):
    holiday_id = serializers.IntegerField(required = True)
    occasion = serializers.CharField(required = True)
    leave_type = serializers.CharField(required = True)
    holiday_date = serializers.DateField(required = True)