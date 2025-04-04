from datetime import datetime, timedelta
from rest_framework import  serializers
from .models import shift
from shifttype.models import shift_type
# from employee.models import employee

class shiftlist_serializer(serializers.ModelSerializer):
    # created_by_name = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField() 

    class Meta:
        model = shift
        fields = "__all__" 

    def get_duration(self, obj):
        if obj.start_time and obj.end_time:
            start = datetime.combine(datetime.today(), obj.start_time)
            end = datetime.combine(datetime.today(), obj.end_time)

            if end <= start:
                end += timedelta(days=1)

            duration = end - start
            hours, remainder = divmod(duration.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            return f"{hours}h {minutes}m"
        return None
    
class shift_serializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(required=False, default=True) 
    shift_type_name = serializers.CharField(write_only=True)
    shift_type_id = serializers.PrimaryKeyRelatedField(queryset=shift_type.objects.all(), write_only=True)
    is_night_shift = serializers.BooleanField(write_only=True, required=False, default=False) # True - "Night Shift" ; False - "Day Shift"
    
    class Meta:
        model = shift
        fields = ["shift_type_name", "shift_type_id", "start_time", "end_time", "is_active", "created_by", "updated_by", "is_night_shift"]
        extra_kwargs = {"created_by": {"read_only": True}, "updated_by": {"read_only": True}}

    def to_internal_value(self, data):
        """
        Convert shift_type_name to shift_type_id before validation.
        """
        shift_type_name = data.get("shift_type_name")
        if shift_type_name:
            try:
                shift_type_obj = shift_type.objects.get(shift_type_name=shift_type_name, is_active = True)
                data["shift_type_id"] = shift_type_obj.shift_type_id
            except shift_type.DoesNotExist:
                raise serializers.ValidationError({"shift_type_name": "Shift Type not found."})
        return super().to_internal_value(data)
    
    def validate(self, data):
        shift_type_id = data.get("shift_type_id")
        start_time = data.get("start_time", self.instance.start_time)
        end_time = data.get("end_time", self.instance.end_time)

        if data['is_night_shift'] == False and (start_time > end_time):
            raise serializers.ValidationError("Start time must be before end time.")
        if shift.objects.filter(shift_type_id=shift_type_id, start_time=start_time, end_time=end_time).exists():
            raise serializers.ValidationError("A shift with this shift type, start time, and end time already exists.")

        return data

    def create(self, validated_data):
        Flag = validated_data.pop("is_night_shift", False)
        shift_type_name = validated_data.pop("shift_type_name", None)
        user = 1 # self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user 
        return shift.objects.create(**validated_data)

    def update(self, instance, validated_data):
        Flag = validated_data.pop("is_night_shift", False)
        shift_type_name = validated_data.pop("shift_type_name", None)
        user = 1 # self.context["request"].user
        validated_data["updated_by"] = user 
        return super().update(instance, validated_data)
    