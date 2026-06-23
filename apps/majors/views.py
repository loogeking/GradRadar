from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Major, ScoreLine, Enrollment, ReferenceBook
from .serializers import (
    MajorListSerializer,
    MajorDetailSerializer,
    ScoreLineSerializer,
    EnrollmentSerializer,
    ReferenceBookSerializer,
)
from .filters import MajorFilter, ScoreLineFilter, EnrollmentFilter


class MajorViewSet(viewsets.ReadOnlyModelViewSet):
    """专业接口"""
    queryset = Major.objects.select_related('college__school').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MajorFilter
    search_fields = ['name', 'code', 'college__name', 'college__school__name']
    ordering_fields = ['code', 'name']
    ordering = ['code']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MajorDetailSerializer
        return MajorListSerializer


class ScoreLineViewSet(viewsets.ReadOnlyModelViewSet):
    """复试分数线接口"""
    queryset = ScoreLine.objects.select_related('major__college__school').all()
    serializer_class = ScoreLineSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ScoreLineFilter
    ordering_fields = ['year', 'total_score']
    ordering = ['-year']


class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    """招生计划接口"""
    queryset = Enrollment.objects.select_related('major__college__school').all()
    serializer_class = EnrollmentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = EnrollmentFilter
    ordering_fields = ['year']
    ordering = ['-year']


class ReferenceBookViewSet(viewsets.ReadOnlyModelViewSet):
    """参考书目接口"""
    queryset = ReferenceBook.objects.select_related('major').all()
    serializer_class = ReferenceBookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['major']
    search_fields = ['book_name', 'author']


class CompareView(APIView):
    """专业对比接口
    GET /api/compare/?ids=1,2,3
    """

    def get(self, request):
        ids_str = request.query_params.get('ids', '')
        if not ids_str:
            return Response(
                {'error': '请提供专业ID列表，格式：?ids=1,2,3'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ids = [int(i) for i in ids_str.split(',') if i.strip()]
        except ValueError:
            return Response(
                {'error': '专业ID必须是数字'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(ids) < 2:
            return Response(
                {'error': '至少需要2个专业进行对比'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(ids) > 5:
            return Response(
                {'error': '最多支持5个专业同时对比'},
                status=status.HTTP_400_BAD_REQUEST
            )

        majors = Major.objects.filter(id__in=ids).select_related('college__school')
        serializer = MajorDetailSerializer(majors, many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })


class TrendView(APIView):
    """专业趋势数据接口（给ECharts用）
    GET /api/trends/<major_id>/
    """

    def get(self, request, major_id):
        try:
            major = Major.objects.select_related('college__school').get(id=major_id)
        except Major.DoesNotExist:
            return Response(
                {'error': '专业不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        score_lines = ScoreLine.objects.filter(major=major).order_by('year')
        enrollments = Enrollment.objects.filter(major=major).order_by('year')

        # 整理为前端图表友好格式
        score_data = {
            'years': [s.year for s in score_lines],
            'total_score': [s.total_score for s in score_lines],
            'politics': [s.politics for s in score_lines],
            'english': [s.english for s in score_lines],
            'math': [s.math for s in score_lines],
            'professional': [s.professional for s in score_lines],
        }

        enrollment_data = {
            'years': [e.year for e in enrollments],
            'plan_total': [e.plan_total for e in enrollments],
            'plan_exam': [e.plan_exam for e in enrollments],
            'plan_recommend': [e.plan_recommend for e in enrollments],
            'recommend_ratio': [e.recommend_ratio for e in enrollments],
        }

        return Response({
            'major': {
                'id': major.id,
                'name': major.name,
                'code': major.code,
                'school_name': major.college.school.name,
                'college_name': major.college.name,
            },
            'score_lines': score_data,
            'enrollments': enrollment_data,
        })