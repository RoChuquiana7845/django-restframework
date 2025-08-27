from django.contrib import admin
from apps.core.admin import BaseModelAdmin
from apps.business.models import Company

@admin.register(Company)
class CompanyAdmin(BaseModelAdmin):
    list_display = ['name', 'code', 'email', 'phone', 'is_active']
    search_fields = ['name', 'code', 'email']
    list_filter = ('is_active', 'created_at')