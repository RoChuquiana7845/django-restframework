from rest_framework import serializers
from apps.core.serializers import BaseModelSerializer
from apps.business.models import Company

class CompanySerializer(BaseModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

    def validate_code(self, value):
        if value:
            value = value.upper().strip()

            if self.instance:
                if Company.objects.exclude(id=self.instance.id).filter(code=value).exists():
                    raise serializers.ValidationError("Ya existe una empresa con este código")
            else:
                if Company.objects.filter(code=value).exists():
                    raise serializers.ValidationError('Ya existe una empresa con este código')
        return value


    def validate_name(self, value):
        if value:
            value = value.upper().strip()
        return value