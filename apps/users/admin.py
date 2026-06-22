from django.contrib import admin
from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'target_type', 'school', 'major', 'created_at']
    list_filter = ['target_type', 'created_at']
    search_fields = ['user__username', 'school__name', 'major__name']
    autocomplete_fields = ['user', 'school', 'major']