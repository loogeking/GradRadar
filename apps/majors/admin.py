from django.contrib import admin
from .models import Major, ScoreLine, Enrollment, ReferenceBook


class ScoreLineInline(admin.TabularInline):
    """在专业详情页内联显示分数线"""
    model = ScoreLine
    extra = 1


class EnrollmentInline(admin.TabularInline):
    """在专业详情页内联显示招生计划"""
    model = Enrollment
    extra = 1


class ReferenceBookInline(admin.TabularInline):
    """在专业详情页内联显示参考书目"""
    model = ReferenceBook
    extra = 1


@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'college', 'degree_type']
    list_filter = ['degree_type', 'college__school']
    search_fields = ['name', 'code', 'college__name', 'college__school__name']
    autocomplete_fields = ['college']
    inlines = [ScoreLineInline, EnrollmentInline, ReferenceBookInline]


@admin.register(ScoreLine)
class ScoreLineAdmin(admin.ModelAdmin):
    list_display = ['id', 'major', 'year', 'total_score', 'politics', 'english', 'math', 'professional']
    list_filter = ['year', 'major__college__school']
    search_fields = ['major__name', 'major__college__school__name']
    autocomplete_fields = ['major']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'major', 'year', 'plan_total', 'plan_exam', 'plan_recommend', 'actual_total', 'recommend_ratio']
    list_filter = ['year', 'major__college__school']
    search_fields = ['major__name', 'major__college__school__name']
    autocomplete_fields = ['major']

    def recommend_ratio(self, obj):
        ratio = obj.recommend_ratio
        return f'{ratio}%' if ratio is not None else '-'
    recommend_ratio.short_description = '推免比例'


@admin.register(ReferenceBook)
class ReferenceBookAdmin(admin.ModelAdmin):
    list_display = ['id', 'book_name', 'author', 'publisher', 'major', 'exam_subject']
    list_filter = ['publisher', 'major__college__school']
    search_fields = ['book_name', 'author', 'major__name']
    autocomplete_fields = ['major']