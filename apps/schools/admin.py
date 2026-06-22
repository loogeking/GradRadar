from django.contrib import admin
from .models import Province, School, College


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'short_name']
    search_fields = ['name', 'short_name']


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'province', 'level', 'is_985', 'is_211', 'is_double_first']
    list_filter = ['province', 'level', 'is_985', 'is_211', 'is_double_first']
    search_fields = ['name', 'code']
    list_editable = ['level', 'is_985', 'is_211', 'is_double_first']
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'code', 'province', 'description')
        }),
        ('层次标签', {
            'fields': ('level', 'is_985', 'is_211', 'is_double_first')
        }),
        ('链接信息', {
            'fields': ('official_url', 'logo_url')
        }),
    )


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'school', 'code', 'url']
    list_filter = ['school__province', 'school']
    search_fields = ['name', 'school__name']
    autocomplete_fields = ['school']