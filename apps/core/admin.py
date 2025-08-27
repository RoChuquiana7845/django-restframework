from django.contrib import admin
from django.utils.html import format_html


class BaseModelAdmin(admin.ModelAdmin):

    list_per_page = 25
    save_on_top = True

    readonly_fields = ('id', 'created_at', 'modified_at', 'created_by', 'updated_by')

    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:
            if hasattr(obj, 'created_at'):
                readonly.extend(['created_at', 'created_by'])
        return readonly

    def save_model(self, request, obj, form, change):
        if not change:
            if hasattr(obj, 'created_by'):
                obj.created_by = request.user
        else:
            if hasattr(obj, 'updated_by'):
                obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))
        if hasattr(self.model, 'is_active'):
            if 'status_badge' not in list_display:
                list_display.append('status_badge')
        return list_display

    def status_badge(self, obj):
        if hasattr(obj, 'is_active'):
            if obj.is_active:
                return format_html('<span style="color: green;">●</span> Activo')
            else:
                return format_html('<span style="color: red;">●</span> Inactivo')
        return '-'

    status_badge.short_description = 'Estado'

    def get_fieldsets(self, request, obj=None):
        if not self.fieldsets:
            fields = [f.name for f in self.model._meta.fields
                      if f.name not in ['id', 'created_at', 'modified_at', 'created_by', 'updated_by']]

            return (
                ('Información Principal', {'fields': fields[:5]}),
                ('Estado', {'fields': ('is_active',)} if 'is_active' in fields else {}),
                ('Auditoría', {
                    'fields': ('id', 'created_at', 'modified_at', 'created_by', 'updated_by'),
                    'classes': ('collapse',)
                }),
            )
        return super().get_fieldsets(request, obj)