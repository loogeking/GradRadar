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
        fields = ['id', 'school', 'school_name', 'name', 'code', 'url']


class SchoolListSerializer(serializers.ModelSerializer):
    """学校列表用（精简）"""
    province_name = serializers.CharField(source='province.name', read_only=True)

    class Meta:
        model = School
        fields = [
            'id', 'name', 'code', 'province', 'province_name',
            'level', 'is_985', 'is_211', 'is_double_first', 'logo_url'
        ]


class SchoolDetailSerializer(serializers.ModelSerializer):
    """学校详情用（含学院）"""
    province_name = serializers.CharField(source='province.name', read_only=True)
    colleges = CollegeSerializer(many=True, read_only=True)
    college_count = serializers.IntegerField(source='colleges.count', read_only=True)

    class Meta:
        model = School
        fields = [
            'id', 'name', 'code', 'province', 'province_name',
            'level', 'is_985', 'is_211', 'is_double_first',
            'official_url', 'logo_url', 'description',
            'colleges', 'college_count',
            'created_at', 'updated_at'
        ]