from django.contrib import admin
from .models import SubjectCategory, SubjectRating


@admin.register(SubjectCategory)
class SubjectCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'category', 'level', 'parent']
    list_filter = ['level', 'category']
    search_fields = ['code', 'name', 'category']


@admin.register(SubjectRating)
class SubjectRatingAdmin(admin.ModelAdmin):
    list_display = ['id', 'school', 'subject', 'rating', 'evaluation_round', 'year']
    list_filter = ['evaluation_round', 'rating', 'year']
    search_fields = ['school__name', 'subject__name', 'subject__code']
    autocomplete_fields = ['school', 'subject']