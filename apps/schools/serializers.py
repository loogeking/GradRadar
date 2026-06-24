from rest_framework import serializers
from .models import Province, School, College


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['id', 'name', 'short_name']


class CollegeSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)

    class Meta:
        model = College
        fields = ['id', 'school', 'school_name', 'name', 'code', 'url', 'platform_id']


class SchoolListSerializer(serializers.ModelSerializer):
    """学校列表用（精简）"""
    province_name = serializers.CharField(source='province.name', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    school_type_display = serializers.CharField(source='get_school_type_display', read_only=True)
    province_area_display = serializers.CharField(source='get_province_area_display', read_only=True)

    class Meta:
        model = School
        fields = [
            'id', 'name', 'code', 'province', 'province_name',
            'level', 'level_display',
            'school_type', 'school_type_display',
            'province_area', 'province_area_display',
            'is_985', 'is_211', 'is_double_first', 'is_self_scoring',
            'logo_url',
        ]


class SchoolDetailSerializer(serializers.ModelSerializer):
    """学校详情用（含学院）"""
    province_name = serializers.CharField(source='province.name', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    school_type_display = serializers.CharField(source='get_school_type_display', read_only=True)
    province_area_display = serializers.CharField(source='get_province_area_display', read_only=True)
    colleges = CollegeSerializer(many=True, read_only=True)
    college_count = serializers.IntegerField(source='colleges.count', read_only=True)
    major_count = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = [
            'id', 'name', 'code', 'province', 'province_name',
            'level', 'level_display',
            'school_type', 'school_type_display',
            'province_area', 'province_area_display',
            'is_985', 'is_211', 'is_double_first', 'is_self_scoring',
            'official_url', 'logo_url', 'description',
            'colleges', 'college_count', 'major_count',
            'created_at', 'updated_at'
        ]

    def get_major_count(self, obj):
        from apps.majors.models import Major
        return Major.objects.filter(college__school=obj).count()