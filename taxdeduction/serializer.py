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


class TaxSlabSerializer(serializers.ModelSerializer):
    class Meta:
        model = tax_slabs
        fields = ['tax_slab_id', 'financial_year', 'tax_regime', 'slab_from', 'slab_to', 'slab_rate', 'is_active']



