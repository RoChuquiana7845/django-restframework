import django_filters
from django.db import models

class BaseFilterSet(django_filters.FilterSet):
    created_date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    created_date_to = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')
    updated_date_from = django_filters.DateFilter(field_name='modified_at', lookup_expr='date__gte')
    updated_date_to = django_filters.DateFilter(field_name='modified_at', lookup_expr='date__lte')
    is_active = django_filters.BooleanFilter()

    class Meta:
        fields = {
            'created_at': ['exact', 'gte', 'lte'],
            'modified_at': ['exact', 'gte', 'lte'],
            'is_active': ['exact'],
        }

    @property
    def qs(self):
        queryset = super().qs

        if hasattr(self._meta.model, 'is_active'):
            if 'is_active' not in self.data:
                queryset = queryset.filter(is_active=True)

        return queryset

class CatalogFilterSet(BaseFilterSet):
    code = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta(BaseFilterSet.Meta):
        fields = BaseFilterSet.Meta.fields.copy()
        fields.update({
            'code': ['exact', 'icontains'],
            'name': ['exact', 'icontains'],
        })