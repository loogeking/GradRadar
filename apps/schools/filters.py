import django_filters
from .models import School


class SchoolFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    province = django_filters.NumberFilter(field_name='province__id')
    province_name = django_filters.CharFilter(field_name='province__name', lookup_expr='icontains')
    level = django_filters.CharFilter(field_name='level')
    is_985 = django_filters.BooleanFilter(field_name='is_985')
    is_211 = django_filters.BooleanFilter(field_name='is_211')
    is_double_first = django_filters.BooleanFilter(field_name='is_double_first')

    class Meta:
        model = School
        fields = ['name', 'province', 'level', 'is_985', 'is_211', 'is_double_first']