from rest_framework import serializers
from .models import financial_year, tax_regimes, tax_slabs

class FinancialYearSerializer(serializers.ModelSerializer):
	class Meta:
		model = financial_year
		fields = '__all__'
		read_only_fields = ['financial_year_id', 'created_at', 'updated_at']


class TaxRegimeSerializer(serializers.ModelSerializer):
	class Meta:
		model = tax_regimes
		fields = '__all__'
		read_only_fields = ['tax_regime_id', 'created_at', 'updated_at']


class TaxSlabSerializer(serializers.Serializer):
	# tax_slab_id = serializers.IntegerField()
	# tax_regime = serializers.CharField()
	slab_from = serializers.DecimalField(max_digits=12, decimal_places=2)
	slab_to = serializers.DecimalField(max_digits=12, decimal_places=2)
	slab_rate = serializers.DecimalField(max_digits=5, decimal_places=2)

	def validate(self, data):
		if data['slab_from'] >= data['slab_to']:
			raise serializers.ValidationError("Slab 'from' value must be less than 'to' value.")
		return data


class TaxSlabUpdateSerializer(serializers.Serializer):
	# tax_slab_id = serializers.IntegerField()
	slab_from = serializers.DecimalField(max_digits=12, decimal_places=2)
	slab_to = serializers.DecimalField(max_digits=12, decimal_places=2)
	slab_rate = serializers.DecimalField(max_digits=5, decimal_places=2)

	def validate(self, data):
		if data['slab_from'] >= data['slab_to']:
			raise serializers.ValidationError("Slab 'from' value must be less than 'to' value.")
		return data
class UpdateTaxregimeSerializer(serializers.Serializer):
	tax_regime_id = serializers.IntegerField()
	


