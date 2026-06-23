from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Notice
from .serializers import NoticeSerializer


class NoticeViewSet(viewsets.ReadOnlyModelViewSet):
    """公告接口"""
    queryset = Notice.objects.select_related('school', 'college').all()
    serializer_class = NoticeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school', 'college', 'notice_type']
    search_fields = ['title', 'content_summary']
    ordering_fields = ['publish_date', 'created_at']
    ordering = ['-publish_date', '-created_at']