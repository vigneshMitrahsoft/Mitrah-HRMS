from .models import Holiday
from rest_framework import serializers
 
class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'
        read_only_fields = ['holiday_id', 'created_at', 'updated_at']
    
class HolidayCreateSerializer(serializers.Serializer):
    occasion = serializers.CharField(required=True)
    leave_type = serializers.CharField(required=True)
    holiday_date = serializers.DateField(required=True)

    def validate(self,data):
        if Holiday.objects.filter(holiday_date = data['holiday_date']).exists():
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

    def update(self, instance, validated_data):
        instance.occasion = validated_data.get('occasion', instance.occasion)
        instance.leave_type = validated_data.get('leave_type', instance.leave_type)
        instance.holiday_date = validated_data.get('holiday_date', instance.holiday_date)
        instance.save()
        return instance