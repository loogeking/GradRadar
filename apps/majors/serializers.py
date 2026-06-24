from rest_framework import serializers
from .models import (
    Major, ResearchDirection, ScoreLine,
    Enrollment, ReferenceBook, NationalScoreLine
)


class ResearchDirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchDirection
        fields = [
            'id', 'year', 'direction_code', 'direction_name',
            'recruit_number', 'is_direction_based',
            'exam_subjects', 'note'
        ]


class ScoreLineSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    score_type_display = serializers.CharField(source='get_score_type_display', read_only=True)
    subject_name = serializers.CharField(source='subject_category.name', read_only=True, default=None)
    subject_code = serializers.CharField(source='subject_category.code', read_only=True, default=None)
    major_name = serializers.CharField(source='major.name', read_only=True, default=None)
    major_code = serializers.CharField(source='major.code', read_only=True, default=None)

    class Meta:
        model = ScoreLine
        fields = [
            'id', 'score_type', 'score_type_display',
            'school', 'school_name', 'year',
            'subject_category', 'subject_name', 'subject_code',
            'major', 'major_name', 'major_code',
            'total_score',
            'politics_score', 'english_score',
            'subject_one_score', 'subject_one_name',
            'subject_two_score', 'subject_two_name',
            'diff_total', 'diff_politics', 'diff_english',
            'diff_subject_one', 'diff_subject_two',
            'source_url', 'note',
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    major_name = serializers.CharField(source='major.name', read_only=True)
    school_name = serializers.CharField(source='major.college.school.name', read_only=True)
    recommend_ratio = serializers.FloatField(read_only=True)
    computed_enroll_ratio = serializers.FloatField(read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'major', 'major_name', 'school_name', 'year',
            'plan_total', 'plan_exam', 'plan_recommend',
            'actual_total', 'actual_exam', 'actual_recommend',
            'apply_count',
            'enroll_ratio', 'avg_score', 'min_score', 'max_score',
            'recommend_ratio', 'computed_enroll_ratio',
            'plan_id', 'source_url', 'note',
        ]


class ReferenceBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferenceBook
        fields = [
            'id', 'major', 'year',
            'book_name', 'author', 'publisher', 'edition',
            'exam_subject', 'raw_text',
        ]


class NationalScoreLineSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject_category.name', read_only=True)
    subject_code = serializers.CharField(source='subject_category.code', read_only=True)

    class Meta:
        model = NationalScoreLine
        fields = [
            'id', 'year', 'area',
            'subject_category', 'subject_code', 'subject_name',
            'total_score', 'politics_score', 'english_score',
            'subject_one_score', 'subject_two_score',
            'source_url', 'note',
        ]


class MajorListSerializer(serializers.ModelSerializer):
    """专业列表用"""
    college_name = serializers.CharField(source='college.name', read_only=True)
    school_name = serializers.CharField(source='college.school.name', read_only=True)
    school_id = serializers.IntegerField(source='college.school.id', read_only=True)
    degree_type_display = serializers.CharField(source='get_degree_type_display', read_only=True)
    learning_type_display = serializers.CharField(source='get_learning_type_display', read_only=True)
    exam_type_display = serializers.CharField(source='get_exam_type_display', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Major
        fields = [
            'id', 'code', 'name',
            'degree_type', 'degree_type_display',
            'learning_type', 'learning_type_display',
            'exam_type', 'exam_type_display',
            'college', 'college_name',
            'school_id', 'school_name',
            'full_name',
        ]

    def get_full_name(self, obj):
        return f'{obj.college.school.name} - {obj.college.name} - {obj.name}'


class MajorDetailSerializer(serializers.ModelSerializer):
    """专业详情用（含研究方向、分数线、招生、参考书）"""
    college_name = serializers.CharField(source='college.name', read_only=True)
    school_name = serializers.CharField(source='college.school.name', read_only=True)
    school_id = serializers.IntegerField(source='college.school.id', read_only=True)
    full_name = serializers.SerializerMethodField()

    degree_type_display = serializers.CharField(source='get_degree_type_display', read_only=True)
    learning_type_display = serializers.CharField(source='get_learning_type_display', read_only=True)
    exam_type_display = serializers.CharField(source='get_exam_type_display', read_only=True)
    doctoral_point_display = serializers.CharField(source='get_doctoral_point_display', read_only=True)

    research_directions = ResearchDirectionSerializer(many=True, read_only=True)
    score_lines = ScoreLineSerializer(many=True, read_only=True)
    enrollments = EnrollmentSerializer(many=True, read_only=True)
    reference_books = ReferenceBookSerializer(many=True, read_only=True)

    subject_info = serializers.SerializerMethodField()
    years_available = serializers.SerializerMethodField()

    class Meta:
        model = Major
        fields = [
            'id', 'code', 'name',
            'degree_type', 'degree_type_display',
            'learning_type', 'learning_type_display',
            'exam_type', 'exam_type_display',
            'doctoral_point', 'doctoral_point_display',
            'college', 'college_name', 'school_id', 'school_name',
            'full_name',
            'research_directions', 'score_lines', 'enrollments', 'reference_books',
            'subject_info', 'years_available',
        ]

    def get_full_name(self, obj):
        return f'{obj.college.school.name} - {obj.college.name} - {obj.name}'

    def get_subject_info(self, obj):
        """该专业所属学科 + 本校在该学科的评级"""
        if not obj.subject_category:
            return None

        from apps.subjects.models import SubjectRating
        rating = SubjectRating.objects.filter(
            school=obj.college.school,
            subject=obj.subject_category
        ).order_by('-evaluation_round').first()

        return {
            'subject_id': obj.subject_category.id,
            'subject_code': obj.subject_category.code,
            'subject_name': obj.subject_category.name,
            'subject_category_name': obj.subject_category.category_name,
            'rating': rating.rating if rating else None,
            'rating_round_display': rating.get_evaluation_round_display() if rating else None,
        }

    def get_years_available(self, obj):
        """有研究方向数据的年份列表"""
        years = obj.research_directions.values_list('year', flat=True).distinct().order_by('-year')
        return list(years)