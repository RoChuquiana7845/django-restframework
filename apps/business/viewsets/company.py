from apps.core.viewset import  BaseModelViewSet
from apps.business.models import Company
from apps.business.serializers.company import  CompanySerializer
from django_filters import rest_framework as filters

class CompanyFilterSet(filters.FilterSet):
    code = filters.CharFilter(lookup_expr='icontains')
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Company
        fields = ['name', 'code', 'is_active']

class CompanyViewSet(BaseModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filterset_class = CompanyFilterSet
    search_fields = ['name', 'code', 'email']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']