from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Major, ResearchDirection, ScoreLine,
    Enrollment, ReferenceBook, NationalScoreLine
)
from .serializers import (
    MajorListSerializer,
    MajorDetailSerializer,
    ResearchDirectionSerializer,
    ScoreLineSerializer,
    EnrollmentSerializer,
    ReferenceBookSerializer,
    NationalScoreLineSerializer,
)
from .filters import MajorFilter, ScoreLineFilter, EnrollmentFilter


class MajorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Major.objects.select_related('college__school', 'subject_category').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MajorFilter
    search_fields = ['name', 'code', 'college__name', 'college__school__name']
    ordering_fields = ['code', 'name']
    ordering = ['code']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MajorDetailSerializer
        return MajorListSerializer


class ResearchDirectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ResearchDirection.objects.select_related('major__college__school').all()
    serializer_class = ResearchDirectionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['major', 'year']
    ordering = ['-year', 'direction_code']


class ScoreLineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ScoreLine.objects.select_related(
        'school', 'subject_category', 'major__college__school'
    ).all()
    serializer_class = ScoreLineSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ScoreLineFilter
    ordering_fields = ['year', 'total_score']
    ordering = ['-year']


class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Enrollment.objects.select_related('major__college__school').all()
    serializer_class = EnrollmentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = EnrollmentFilter
    ordering_fields = ['year']
    ordering = ['-year']


class ReferenceBookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReferenceBook.objects.select_related('major').all()
    serializer_class = ReferenceBookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['major', 'year']
    search_fields = ['book_name', 'author']


class NationalScoreLineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NationalScoreLine.objects.select_related('subject_category').all()
    serializer_class = NationalScoreLineSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['year', 'area', 'subject_category']


class CompareView(APIView):
    """专业对比"""

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
            return Response({'error': '专业ID必须是数字'},
                            status=status.HTTP_400_BAD_REQUEST)

        if len(ids) < 2:
            return Response({'error': '至少需要2个专业进行对比'},
                            status=status.HTTP_400_BAD_REQUEST)
        if len(ids) > 5:
            return Response({'error': '最多支持5个专业同时对比'},
                            status=status.HTTP_400_BAD_REQUEST)

        majors = Major.objects.filter(id__in=ids).select_related(
            'college__school', 'subject_category'
        )
        serializer = MajorDetailSerializer(majors, many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })


class TrendView(APIView):
    """专业历年趋势数据"""

    def get(self, request, major_id):
        try:
            major = Major.objects.select_related('college__school').get(id=major_id)
        except Major.DoesNotExist:
            return Response({'error': '专业不存在'}, status=status.HTTP_404_NOT_FOUND)

        # 专业线
        score_lines = ScoreLine.objects.filter(
            major=major, score_type='major'
        ).order_by('year')

        # 招生
        enrollments = Enrollment.objects.filter(major=major).order_by('year')

        score_data = {
            'years': [s.year for s in score_lines],
            'total_score': [s.total_score for s in score_lines],
            'politics': [s.politics_score for s in score_lines],
            'english': [s.english_score for s in score_lines],
            'subject_one': [s.subject_one_score for s in score_lines],
            'subject_two': [s.subject_two_score for s in score_lines],
        }

        enrollment_data = {
            'years': [e.year for e in enrollments],
            'plan_total': [e.plan_total for e in enrollments],
            'plan_exam': [e.plan_exam for e in enrollments],
            'plan_recommend': [e.plan_recommend for e in enrollments],
            'actual_total': [e.actual_total for e in enrollments],
            'enroll_ratio': [e.enroll_ratio for e in enrollments],
            'avg_score': [e.avg_score for e in enrollments],
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