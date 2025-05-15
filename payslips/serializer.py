from rest_framework import serializers
from .models import Payslip

class PayslipStatusUpdateSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=50)

    def validate(self, data):
        status = data.get('status').strip().lower()
        if status not in ('pending','finalized'):
            raise serializers.ValidationError("Status can only be pending, approved or rejected")
        return data
    

class PayslipSerializer(serializers.ModelSerializer):
	class Meta:
		model = Payslip
		fields = '__all__'
		read_only_fields = ['payslip_id', 'created_at', 'updated_at', 'updated_by']