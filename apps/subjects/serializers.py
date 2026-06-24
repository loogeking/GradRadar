from rest_framework import serializers
from .models import SubjectCategory, SubjectRating


class SubjectRatingSerializer(serializers.ModelSerializer):
    school_id = serializers.IntegerField(source='school.id', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    school_province = serializers.CharField(source='school.province.name', read_only=True)
    school_is_985 = serializers.BooleanField(source='school.is_985', read_only=True)
    school_is_211 = serializers.BooleanField(source='school.is_211', read_only=True)
    school_is_self_scoring = serializers.BooleanField(source='school.is_self_scoring', read_only=True)
    round_display = serializers.CharField(source='get_evaluation_round_display', read_only=True)
    rating_score = serializers.IntegerField(read_only=True)

    class Meta:
        model = SubjectRating
        fields = [
            'id', 'rating', 'evaluation_round', 'round_display', 'rating_score',
            'year', 'source_url', 'note',
            'school_id', 'school_name', 'school_province',
            'school_is_985', 'school_is_211', 'school_is_self_scoring',
        ]


class SubjectCategorySimpleSerializer(serializers.ModelSerializer):
    """学科简略（用于嵌套）"""
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model = SubjectCategory
        fields = ['id', 'code', 'name', 'level', 'level_display',
                  'category_code', 'category_name']


class SubjectListSerializer(serializers.ModelSerializer):
    """学科列表用"""
    rating_count = serializers.SerializerMethodField()
    major_count = serializers.SerializerMethodField()
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model = SubjectCategory
        fields = [
            'id', 'code', 'name',
            'category_code', 'category_name',
            'level', 'level_display',
            'is_academic', 'is_self_set',
            'rating_count', 'major_count',
        ]

    def get_rating_count(self, obj):
        return obj.ratings.values('school').distinct().count()

    def get_major_count(self, obj):
        return obj.majors.count()


class SubjectDetailSerializer(serializers.ModelSerializer):
    """学科详情用（含评级 + 招生专业）"""
    ratings = serializers.SerializerMethodField()
    majors_by_school = serializers.SerializerMethodField()
    parent = SubjectCategorySimpleSerializer(read_only=True)
    children = SubjectCategorySimpleSerializer(many=True, read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model = SubjectCategory
        fields = [
            'id', 'code', 'name',
            'category_code', 'category_name',
            'level', 'level_display',
            'is_academic', 'is_self_set',
            'description',
            'parent', 'children',
            'ratings', 'majors_by_school',
        ]

    def get_ratings(self, obj):
        qs = obj.ratings.select_related('school', 'school__province').all()
        latest = {}
        priority = {'round_5': 2, 'round_4': 1}
        for r in qs:
            key = r.school_id
            if key not in latest or priority.get(r.evaluation_round, 0) > priority.get(latest[key].evaluation_round, 0):
                latest[key] = r
        ratings = list(latest.values())
        ratings.sort(key=lambda x: x.rating_score, reverse=True)
        return SubjectRatingSerializer(ratings, many=True).data

    def get_majors_by_school(self, obj):
        majors = obj.majors.select_related('college__school__province').all()

        school_dict = {}
        for m in majors:
            school = m.college.school
            sid = school.id
            if sid not in school_dict:
                school_dict[sid] = {
                    'school_id': school.id,
                    'school_name': school.name,
                    'school_province': school.province.name if school.province else '',
                    'school_is_985': school.is_985,
                    'school_is_211': school.is_211,
                    'school_is_self_scoring': school.is_self_scoring,
                    'rating': None,
                    'majors': []
                }
            school_dict[sid]['majors'].append({
                'major_id': m.id,
                'major_code': m.code,
                'major_name': m.name,
                'college_name': m.college.name,
                'degree_type': m.degree_type,
                'degree_type_display': m.get_degree_type_display(),
                'learning_type': m.learning_type,
                'learning_type_display': m.get_learning_type_display(),
                'exam_type': m.exam_type,
                'exam_type_display': m.get_exam_type_display(),
            })

        # 补充评级
        ratings = SubjectRating.objects.filter(
            school_id__in=school_dict.keys(),
            subject=obj
        ).order_by('-evaluation_round')
        for r in ratings:
            if school_dict[r.school_id]['rating'] is None:
                school_dict[r.school_id]['rating'] = r.rating

        score_map = {'A+': 9, 'A': 8, 'A-': 7, 'B+': 6, 'B': 5, 'B-': 4, 'C+': 3, 'C': 2, 'C-': 1}
        result = list(school_dict.values())
        result.sort(key=lambda x: score_map.get(x['rating'], 0), reverse=True)
        return result