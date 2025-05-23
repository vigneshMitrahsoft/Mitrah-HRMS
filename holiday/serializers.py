from .models import holiday
from rest_framework import serializers
 
class holiday_serializer(serializers.ModelSerializer):
	class Meta:
		model = holiday
		fields = '__all__'
		read_only_fields = [
			'holiday_id',
			'created_at',
			'updated_at'
		]
	
class holiday_create_serializer(serializers.Serializer):
	occasion = serializers.CharField(required = True)
	leave_type = serializers.CharField(required = True)
	holiday_date = serializers.DateField(required = True)

	def validate(self,data):
		if holiday.objects.filter(holiday_date = data['holiday_date']).exists():
			raise serializers.ValidationError("Holiday date already exists")
		return data

class holiday_update_serializer(serializers.Serializer):
	holiday_id = serializers.IntegerField(required = True)
	occasion = serializers.CharField(required = True)
	leave_type = serializers.CharField(required = True)
	holiday_date = serializers.DateField(required = True)
	
class excel_serializer(serializers.Serializer):
	excel_file = serializers.FileField()

	def validate_excel_file(self, value):
		if not value.name.endswith(('.xlsx', '.xls')):
			raise serializers.ValidationError("Only Excel files are allowed.")
		return value
