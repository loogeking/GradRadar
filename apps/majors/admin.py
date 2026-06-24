from django.contrib import admin
from .models import (
    Major, ResearchDirection, ScoreLine,
    Enrollment, ReferenceBook, NationalScoreLine
)


class ResearchDirectionInline(admin.TabularInline):
    model = ResearchDirection
    extra = 0
    fields = ['year', 'direction_code', 'direction_name', 'recruit_number']


class ScoreLineInline(admin.TabularInline):
    model = ScoreLine
    extra = 0
    fields = ['year', 'score_type', 'total_score',
              'politics_score', 'english_score',
              'subject_one_score', 'subject_two_score']
    fk_name = 'major'


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    fields = ['year', 'plan_total', 'plan_recommend',
              'actual_total', 'enroll_ratio', 'avg_score']


class ReferenceBookInline(admin.TabularInline):
    model = ReferenceBook
    extra = 0
    fields = ['year', 'book_name', 'author', 'publisher', 'exam_subject']


@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'code', 'college',
        'degree_type', 'learning_type', 'subject_category', 'platform_id'
    ]
    list_filter = [
        'degree_type', 'learning_type', 'exam_type',
        'college__school'
    ]
    search_fields = [
        'name', 'code', 'college__name',
        'college__school__name', 'platform_id'
    ]
    autocomplete_fields = ['college', 'subject_category']
    inlines = [
        ResearchDirectionInline,
        ScoreLineInline,
        EnrollmentInline,
        ReferenceBookInline,
    ]
    fieldsets = (
        ('基本信息', {
            'fields': ('college', 'code', 'name', 'degree_type', 'subject_category')
        }),
        ('招生属性', {
            'fields': ('learning_type', 'exam_type', 'doctoral_point')
        }),
        ('采集元数据', {
            'fields': ('platform_id',),
            'classes': ('collapse',),
        }),
    )


@admin.register(ResearchDirection)
class ResearchDirectionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'major', 'year', 'direction_code', 'direction_name',
        'recruit_number', 'is_direction_based'
    ]
    list_filter = ['year', 'is_direction_based', 'major__college__school']
    search_fields = ['direction_name', 'major__name', 'major__college__school__name']
    autocomplete_fields = ['major']


@admin.register(ScoreLine)
class ScoreLineAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'school', 'score_type', 'year',
        'total_score', 'politics_score', 'english_score',
        'subject_one_score', 'subject_two_score',
        'subject_category', 'major',
    ]
    list_filter = [
        'score_type', 'year', 'school'
    ]
    search_fields = [
        'school__name', 'subject_category__name',
        'major__name', 'major__college__school__name'
    ]
    autocomplete_fields = ['school', 'subject_category', 'major']
    fieldsets = (
        ('归属', {
            'fields': ('school', 'score_type', 'subject_category', 'major', 'year')
        }),
        ('分数', {
            'fields': (
                'total_score',
                'politics_score', 'english_score',
                'subject_one_score', 'subject_one_name',
                'subject_two_score', 'subject_two_name',
            )
        }),
        ('与国家线差值', {
            'fields': (
                'diff_total',
                'diff_politics', 'diff_english',
                'diff_subject_one', 'diff_subject_two',
            ),
            'classes': ('collapse',),
        }),
        ('元信息', {
            'fields': ('source_url', 'note')
        }),
    )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'major', 'year',
        'plan_total', 'plan_recommend', 'actual_total',
        'apply_count', 'enroll_ratio', 'avg_score',
        'recommend_ratio',
    ]
    list_filter = ['year', 'major__college__school']
    search_fields = ['major__name', 'major__college__school__name']
    autocomplete_fields = ['major']
    fieldsets = (
        ('基本信息', {
            'fields': ('major', 'year')
        }),
        ('计划数', {
            'fields': ('plan_total', 'plan_exam', 'plan_recommend')
        }),
        ('实际录取', {
            'fields': ('actual_total', 'actual_exam', 'actual_recommend')
        }),
        ('报名与统计', {
            'fields': ('apply_count', 'enroll_ratio',
                       'avg_score', 'min_score', 'max_score')
        }),
        ('元信息', {
            'fields': ('plan_id', 'source_url', 'note')
        }),
    )

    def recommend_ratio(self, obj):
        ratio = obj.recommend_ratio
        return f'{ratio}%' if ratio is not None else '-'
    recommend_ratio.short_description = '推免比例'


@admin.register(ReferenceBook)
class ReferenceBookAdmin(admin.ModelAdmin):
    list_display = ['id', 'book_name', 'author', 'publisher',
                    'major', 'year', 'exam_subject']
    list_filter = ['year', 'publisher', 'major__college__school']
    search_fields = ['book_name', 'author', 'major__name']
    autocomplete_fields = ['major']


@admin.register(NationalScoreLine)
class NationalScoreLineAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'year', 'area', 'subject_category',
        'total_score', 'politics_score', 'english_score',
        'subject_one_score', 'subject_two_score'
    ]
    list_filter = ['year', 'area']
    search_fields = ['subject_category__name', 'subject_category__code']
    autocomplete_fields = ['subject_category']