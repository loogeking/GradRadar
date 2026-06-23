from rest_framework import serializers
from .models import Major, ScoreLine, Enrollment, ReferenceBook


class ScoreLineSerializer(serializers.ModelSerializer):
    major_name = serializers.CharField(source='major.name', read_only=True)
    school_name = serializers.CharField(source='major.college.school.name', read_only=True)

    class Meta:
        model = ScoreLine
        fields = [
            'id', 'major', 'major_name', 'school_name',
            'year', 'total_score', 'politics', 'english',
            'math', 'professional', 'source_url', 'note'
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    major_name = serializers.CharField(source='major.name', read_only=True)
    school_name = serializers.CharField(source='major.college.school.name', read_only=True)
    recommend_ratio = serializers.FloatField(read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'major', 'major_name', 'school_name',
            'year', 'plan_total', 'plan_exam', 'plan_recommend',
            'actual_total', 'apply_count', 'recommend_ratio',
            'source_url', 'note'
        ]


class ReferenceBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferenceBook
        fields = [
            'id', 'major', 'book_name', 'author',
            'publisher', 'edition', 'exam_subject'
        ]


class MajorListSerializer(serializers.ModelSerializer):
    """专业列表用"""
    college_name = serializers.CharField(source='college.name', read_only=True)
    school_name = serializers.CharField(source='college.school.name', read_only=True)
    school_id = serializers.IntegerField(source='college.school.id', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Major
        fields = [
            'id', 'code', 'name', 'degree_type',
            'college', 'college_name',
            'school_id', 'school_name',
            'full_name',
        ]

    def get_full_name(self, obj):
        """完整名称：学校 - 学院 - 专业"""
        return f'{obj.college.school.name} - {obj.college.name} - {obj.name}'


class MajorDetailSerializer(serializers.ModelSerializer):
    """专业详情用（含分数线、招生、参考书、学科评级）"""
    college_name = serializers.CharField(source='college.name', read_only=True)
    school_name = serializers.CharField(source='college.school.name', read_only=True)
    school_id = serializers.IntegerField(source='college.school.id', read_only=True)
    full_name = serializers.SerializerMethodField()
    score_lines = ScoreLineSerializer(many=True, read_only=True)
    enrollments = EnrollmentSerializer(many=True, read_only=True)
    reference_books = ReferenceBookSerializer(many=True, read_only=True)

    # 学科信息和评级
    subject_info = serializers.SerializerMethodField()

    class Meta:
        model = Major
        fields = [
            'id', 'code', 'name', 'degree_type',
            'college', 'college_name', 'school_id', 'school_name',
            'full_name',
            'research_direction', 'exam_subjects',
            'score_lines', 'enrollments', 'reference_books',
            'subject_info',
        ]

    def get_full_name(self, obj):
        return f'{obj.college.school.name} - {obj.college.name} - {obj.name}'

    def get_subject_info(self, obj):
        """该专业所属学科 + 本校在该学科的评级"""
        if not obj.subject_category:
            return None

        from apps.subjects.models import SubjectRating
        # 找到本校在这个学科的最新评级
        rating = SubjectRating.objects.filter(
            school=obj.college.school,
            subject=obj.subject_category
        ).order_by('-evaluation_round').first()

        return {
            'subject_id': obj.subject_category.id,
            'subject_code': obj.subject_category.code,
            'subject_name': obj.subject_category.name,
            'subject_category': obj.subject_category.category,
            'rating': rating.rating if rating else None,
            'rating_round_display': rating.get_evaluation_round_display() if rating else None,
        }