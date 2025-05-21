from rest_framework import  serializers
from .models import *


class shift_type_serializer(serializers.ModelSerializer):
	is_active = serializers.BooleanField(required=False, default=True) 
	created_at = serializers.DateTimeField(format="%Y-%m-%d %-I:%M %p")
	updated_at = serializers.DateTimeField(format="%Y-%m-%d %-I:%M %p")

	class Meta:
		model = shift_type 
		fields = ["shift_type_name", "description", "created_by", "updated_by", "is_active", "created_by", "updated_by"]
		extra_kwargs = {"created_by": {"read_only": True}, "updated_by": {"read_only": True}}
	
	def validate(self, data):
		if shift_type.objects.filter(shift_type_name=data['shift_type_name']).exists():
			raise serializers.ValidationError("A shift type already exists.")
		return data

	def create(self, validated_data):
		user = 1 #self.context["request"].user
		validated_data["created_by"] = user
		validated_data["updated_by"] = user 
		return shift_type.objects.create(**validated_data)

	def update(self, instance, validated_data):
		user = 1 #self.context["request"].user
		validated_data["updated_by"] = user 
		return super().update(instance, validated_data)
	

class Shift_type_list_serializer(serializers.ModelSerializer):
	# created_by_name = serializers.SerializerMethodField()

	created_at = serializers.DateTimeField(format="%Y-%m-%d %-I:%M %p")
	updated_at = serializers.DateTimeField(format="%Y-%m-%d %-I:%M %p")
	class Meta:
		model = shift_type
		fields = "__all__" #["shift_type_name", "description", "created_by", "updated_by"] #, "created_by_name"]

