from django.contrib import admin
from .models import Notice


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'school', 'college', 'notice_type', 'publish_date', 'created_at']
    list_filter = ['notice_type', 'school__province', 'school', 'publish_date']
    search_fields = ['title', 'school__name', 'content_summary']
    autocomplete_fields = ['school', 'college']
    date_hierarchy = 'publish_date'