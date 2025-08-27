from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone


class BaseModelSerializer(serializers.ModelSerializer):

    created_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    modified_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True)

    class Meta:
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'modified_at', 'created_by', 'updated_by')

    def to_representation(self, instance):
        data = super().to_representation(instance)

        for field in ['created_at', 'modified_at']:
            if data.get(field) is None:
                data[field] = None

        return data


class CatalogSerializer(BaseModelSerializer):

    class Meta:
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'modified_at', 'created_by', 'updated_by')

    def validate_code(self, value):
        if value:
            value = value.upper().strip()

            model = self.Meta.model
            if self.instance:
                if model.objects.exclude(id=self.instance.id).filter(code=value).exists():
                    raise serializers.ValidationError("Ya existe un registro con este código.")
            else:
                if model.objects.filter(code=value).exists():
                    raise serializers.ValidationError("Ya existe un registro con este código.")

        return value

    def validate_name(self, value):
        if value:
            value = value.strip().title()
        return value


class PersonSerializer(BaseModelSerializer):

    nombre_completo = serializers.CharField(read_only=True)

    class Meta:
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'modified_at', 'created_by', 'updated_by')

    def validate_cedula(self, value):
        if not value or len(value) != 10 or not value.isdigit():
            raise serializers.ValidationError("La cédula debe tener 10 dígitos.")

        coefficients = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        total = 0

        for i in range(9):
            product = int(value[i]) * coefficients[i]
            if product > 9:
                product -= 9
            total += product

        verificador = (10 - (total % 10)) % 10

        if verificador != int(value[9]):
            raise serializers.ValidationError("La cédula ingresada no es válida.")

        return value

    def validate_email(self, value):
        if value:
            model = self.Meta.model
            if self.instance:
                if model.objects.exclude(id=self.instance.id).filter(email=value).exists():
                    raise serializers.ValidationError("Ya existe una persona con este email.")
            else:
                if model.objects.filter(email=value).exists():
                    raise serializers.ValidationError("Ya existe una persona con este email.")
        return value

    def validate(self, attrs):
        if 'nombres' in attrs:
            attrs['nombres'] = attrs['nombres'].strip().title()
        if 'apellidos' in attrs:
            attrs['apellidos'] = attrs['apellidos'].strip().title()

        return attrs


class CompanySerializer(BaseModelSerializer):

    class Meta:
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'modified_at', 'created_by', 'updated_by')

    def validate_ruc(self, value):
        if not value or len(value) != 13 or not value.isdigit():
            raise serializers.ValidationError("El RUC debe tener 13 dígitos.")

        if not value.endswith('001'):
            raise serializers.ValidationError("El RUC debe terminar en 001.")

        return value

    def validate(self, attrs):
        text_fields = ['razon_social', 'nombre_comercial']
        for field in text_fields:
            if field in attrs and attrs[field]:
                attrs[field] = attrs[field].strip().title()

        return attrs


class ReadOnlySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        fields = '__all__'

    def create(self, validated_data):
        raise serializers.ValidationError("Este serializer es solo de lectura.")

    def update(self, instance, validated_data):
        raise serializers.ValidationError("Este serializer es solo de lectura.")


class BulkListSerializer(serializers.ListSerializer):

    def create(self, validated_data):
        instances = []
        errors = []

        for i, item_data in enumerate(validated_data):
            try:
                instance = self.child.Meta.model(**item_data)
                instance.full_clean()
                instances.append(instance)
            except Exception as e:
                errors.append({
                    'index': i,
                    'data': item_data,
                    'error': str(e)
                })

        if errors:
            raise serializers.ValidationError({
                'bulk_errors': errors
            })

        return self.child.Meta.model.objects.bulk_create(instances)

    def update(self, instances, validated_data):
        instance_mapping = {instance.id: instance for instance in instances}
        data_mapping = {item['id']: item for item in validated_data if 'id' in item}

        updated_instances = []

        for instance_id, data in data_mapping.items():
            instance = instance_mapping.get(instance_id)
            if instance:
                for attr, value in data.items():
                    setattr(instance, attr, value)
                updated_instances.append(instance)

        if updated_instances:
            self.child.Meta.model.objects.bulk_update(
                updated_instances,
                [field.name for field in self.child.Meta.model._meta.fields if not field.primary_key]
            )

        return updated_instances


class TimestampMixin:

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if hasattr(instance, 'created_at') and instance.created_at:
            data['created_at_formatted'] = instance.created_at.strftime('%d/%m/%Y %H:%M')
        if hasattr(instance, 'modified_at') and instance.modified_at:
            data['modified_at_formatted'] = instance.modified_at.strftime('%d/%m/%Y %H:%M')

        return data


class StatusMixin:

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if hasattr(instance, 'is_active'):
            data['status_display'] = 'Activo' if instance.is_active else 'Inactivo'

        return data


class NestedRelationMixin:

    def __init__(self, *args, **kwargs):
        self.nested_fields = kwargs.pop('nested_fields', {})
        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        for field_name, config in self.nested_fields.items():
            if hasattr(instance, field_name):
                related_obj = getattr(instance, field_name)
                if related_obj:
                    nested_data = {}
                    for attr in config.get('fields', ['id', 'name']):
                        if hasattr(related_obj, attr):
                            nested_data[attr] = getattr(related_obj, attr)
                    data[f"{field_name}_detail"] = nested_data

        return data