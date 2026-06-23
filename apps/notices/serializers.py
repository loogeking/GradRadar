from rest_framework import serializers
from .models import Notice


class NoticeSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    college_name = serializers.CharField(source='college.name', read_only=True, default=None)
    notice_type_display = serializers.CharField(source='get_notice_type_display', read_only=True)

    class Meta:
        model = Notice
        fields = [
            'id', 'title', 'url', 'publish_date',
            'notice_type', 'notice_type_display',
            'school', 'school_name', 'college', 'college_name',
            'content_summary', 'created_at'
        ]