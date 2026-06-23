from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Province, School, College
from .serializers import (
    ProvinceSerializer,
    SchoolListSerializer,
    SchoolDetailSerializer,
    CollegeSerializer,
)
from .filters import SchoolFilter


class ProvinceViewSet(viewsets.ReadOnlyModelViewSet):
    """省份只读接口"""
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    pagination_class = None  # 省份不分页


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    """院校接口
    - GET /api/schools/                列表（支持筛选/搜索）
    - GET /api/schools/<id>/           详情（含学院）
    """
    queryset = School.objects.select_related('province').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SchoolFilter
    search_fields = ['name', 'code', 'province__name']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['code']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SchoolDetailSerializer
        return SchoolListSerializer


class CollegeViewSet(viewsets.ReadOnlyModelViewSet):
    """学院接口
    - GET /api/colleges/?school=<id>
    """
    queryset = College.objects.select_related('school').all()
    serializer_class = CollegeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['school']
    search_fields = ['name', 'school__name']