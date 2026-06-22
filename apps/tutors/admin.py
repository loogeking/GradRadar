from django.contrib import admin
from .models import Tutor


@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'title', 'college', 'is_doctoral_supervisor', 'email']
    list_filter = ['title', 'is_doctoral_supervisor', 'college__school']
    search_fields = ['name', 'research_area', 'college__name', 'college__school__name']
    autocomplete_fields = ['college']
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'title', 'college', 'is_doctoral_supervisor')
        }),
        ('研究信息', {
            'fields': ('research_area', 'bio')
        }),
        ('联系方式', {
            'fields': ('email', 'homepage')
        }),
    )