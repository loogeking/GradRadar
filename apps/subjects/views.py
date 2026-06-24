from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import SubjectCategory, SubjectRating
from .serializers import (
    SubjectListSerializer,
    SubjectDetailSerializer,
    SubjectRatingSerializer,
)


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    """学科接口"""
    queryset = SubjectCategory.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['level', 'category_code', 'is_academic', 'is_self_set']
    search_fields = ['code', 'name', 'category_name']
    ordering_fields = ['code', 'name']
    ordering = ['code']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SubjectDetailSerializer
        return SubjectListSerializer


class SubjectRatingViewSet(viewsets.ReadOnlyModelViewSet):
    """学科评级接口"""
    queryset = SubjectRating.objects.select_related('school', 'subject').all()
    serializer_class = SubjectRatingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['school', 'subject', 'evaluation_round', 'rating']