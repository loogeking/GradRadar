from django.contrib import admin
from .models import SubjectCategory, SubjectRating


@admin.register(SubjectCategory)
class SubjectCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'code', 'name', 'level', 'category_name',
        'is_academic', 'is_self_set', 'parent'
    ]
    list_filter = ['level', 'category_code', 'is_academic', 'is_self_set']
    search_fields = ['code', 'name', 'category_name']
    autocomplete_fields = ['parent']


@admin.register(SubjectRating)
class SubjectRatingAdmin(admin.ModelAdmin):
    list_display = ['id', 'school', 'subject', 'rating', 'evaluation_round', 'year']
    list_filter = ['evaluation_round', 'rating', 'year']
    search_fields = ['school__name', 'subject__name', 'subject__code']
    autocomplete_fields = ['school', 'subject']