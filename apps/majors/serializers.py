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

    class Meta:
        model = Major
        fields = [
            'id', 'code', 'name', 'degree_type',
            'college', 'college_name', 'school_id', 'school_name'
        ]


class MajorDetailSerializer(serializers.ModelSerializer):
    """专业详情用（含分数线、招生、参考书）"""
    college_name = serializers.CharField(source='college.name', read_only=True)
    school_name = serializers.CharField(source='college.school.name', read_only=True)
    school_id = serializers.IntegerField(source='college.school.id', read_only=True)
    score_lines = ScoreLineSerializer(many=True, read_only=True)
    enrollments = EnrollmentSerializer(many=True, read_only=True)
    reference_books = ReferenceBookSerializer(many=True, read_only=True)

    class Meta:
        model = Major
        fields = [
            'id', 'code', 'name', 'degree_type',
            'college', 'college_name', 'school_id', 'school_name',
            'research_direction', 'exam_subjects',
            'score_lines', 'enrollments', 'reference_books'
        ]