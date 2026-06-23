from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Tutor
from .serializers import TutorSerializer


class TutorViewSet(viewsets.ReadOnlyModelViewSet):
    """导师接口"""
    queryset = Tutor.objects.select_related('college__school').all()
    serializer_class = TutorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['college', 'title', 'is_doctoral_supervisor', 'college__school']
    search_fields = ['name', 'research_area', 'college__name']
    ordering_fields = ['name']
    ordering = ['name']