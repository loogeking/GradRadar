import django_filters
from .models import Major, ScoreLine, Enrollment


class MajorFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    code = django_filters.CharFilter(field_name='code', lookup_expr='startswith')
    school = django_filters.NumberFilter(field_name='college__school__id')
    college = django_filters.NumberFilter(field_name='college__id')
    degree_type = django_filters.CharFilter(field_name='degree_type')

    class Meta:
        model = Major
        fields = ['name', 'code', 'school', 'college', 'degree_type']


class ScoreLineFilter(django_filters.FilterSet):
    major = django_filters.NumberFilter(field_name='major__id')
    school = django_filters.NumberFilter(field_name='major__college__school__id')
    year = django_filters.NumberFilter(field_name='year')
    year_min = django_filters.NumberFilter(field_name='year', lookup_expr='gte')
    year_max = django_filters.NumberFilter(field_name='year', lookup_expr='lte')
    score_min = django_filters.NumberFilter(field_name='total_score', lookup_expr='gte')
    score_max = django_filters.NumberFilter(field_name='total_score', lookup_expr='lte')

    class Meta:
        model = ScoreLine
        fields = ['major', 'school', 'year']


class EnrollmentFilter(django_filters.FilterSet):
    major = django_filters.NumberFilter(field_name='major__id')
    school = django_filters.NumberFilter(field_name='major__college__school__id')
    year = django_filters.NumberFilter(field_name='year')

    class Meta:
        model = Enrollment
        fields = ['major', 'school', 'year']