from rest_framework import serializers
from .models import Tutor


class TutorSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    school_name = serializers.CharField(source='college.school.name', read_only=True)
    title_display = serializers.CharField(source='get_title_display', read_only=True)

    class Meta:
        model = Tutor
        fields = [
            'id', 'name', 'title', 'title_display',
            'college', 'college_name', 'school_name',
            'research_area', 'email', 'homepage',
            'is_doctoral_supervisor', 'bio'
        ]