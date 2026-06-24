from django.contrib import admin
from .models import Province, School, College


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'short_name']
    search_fields = ['name', 'short_name']


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'code', 'province',
        'level', 'school_type', 'province_area',
        'is_985', 'is_211', 'is_double_first', 'is_self_scoring',
        'platform_id',
    ]
    list_filter = [
        'province', 'level', 'school_type', 'province_area',
        'is_985', 'is_211', 'is_double_first', 'is_self_scoring',
    ]
    search_fields = ['name', 'code', 'platform_id']
    list_editable = ['level', 'is_985', 'is_211', 'is_double_first', 'is_self_scoring']
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'code', 'province', 'description')
        }),
        ('层次标签', {
            'fields': ('level', 'is_985', 'is_211', 'is_double_first',
                       'is_self_scoring', 'school_type', 'province_area')
        }),
        ('链接信息', {
            'fields': ('official_url', 'logo_url')
        }),
        ('采集元数据', {
            'fields': ('platform_id',),
            'classes': ('collapse',),
        }),
    )


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'school', 'code', 'platform_id']
    list_filter = ['school__province', 'school']
    search_fields = ['name', 'school__name', 'platform_id']
    autocomplete_fields = ['school']