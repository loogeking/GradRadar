"""
数据入库管道
负责把适配器输出的标准数据写入数据库
"""
import os
import sys
import django
from pathlib import Path

# 设置 Django 环境
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.schools.models import Province, School, College
from apps.subjects.models import SubjectCategory, SubjectRating
from apps.majors.models import (
    Major, ResearchDirection, ScoreLine,
    Enrollment, ReferenceBook, NationalScoreLine
)
from apps.notices.models import Notice


class Pipeline:
    """数据入库管道"""

    def __init__(self, logger=None):
        self.logger = logger
        self.stats = {
            'schools': {'new': 0, 'updated': 0, 'skipped': 0},
            'colleges': {'new': 0, 'updated': 0, 'skipped': 0},
            'majors': {'new': 0, 'updated': 0, 'skipped': 0},
            'research_directions': {'new': 0, 'updated': 0, 'skipped': 0},
            'score_lines': {'new': 0, 'updated': 0, 'skipped': 0},
            'enrollments': {'new': 0, 'updated': 0, 'skipped': 0},
            'reference_books': {'new': 0, 'updated': 0, 'skipped': 0},
            'subject_ratings': {'new': 0, 'updated': 0, 'skipped': 0},
            'notices': {'new': 0, 'updated': 0, 'skipped': 0},
        }

    def log(self, msg, level='info'):
        if self.logger:
            getattr(self.logger, level)(msg)
        else:
            print(f'[{level.upper()}] {msg}')
    # ============== 学科兜底 ==============

    def _get_or_create_subject(self, code, name_hint=None):
        """
        根据学科代码获取，找不到时自动创建占位记录
        :param code: 学科代码
        :param name_hint: 名称提示（用于自动创建时的名字）
        """
        if not code:
            return None

        subject = SubjectCategory.objects.filter(code=code).first()
        if subject:
            return subject

        # 兜底创建
        code = str(code).strip()
        category_code = code[:2] if len(code) >= 2 else ''

        # 判断层级
        if len(code) == 2:
            level = 'category'
            is_academic = True
        elif len(code) == 4:
            # 第3位 < '5' 一般是学硕一级学科，>= '5' 一般是专硕类别
            third_char = code[2] if len(code) >= 3 else '0'
            if third_char < '5':
                level = 'first_class'
                is_academic = True
            else:
                level = 'professional_category'
                is_academic = False
        elif len(code) == 6:
            third_char = code[2] if len(code) >= 3 else '0'
            if third_char < '5':
                level = 'second_class'
                is_academic = True
            else:
                level = 'professional_field'
                is_academic = False
        else:
            level = 'second_class'
            is_academic = True

        # 找父级
        parent = None
        if len(code) == 4:
            parent = SubjectCategory.objects.filter(code=code[:2]).first()
        elif len(code) == 6:
            parent = SubjectCategory.objects.filter(code=code[:4]).first()

        # 找门类
        category_name = ''
        if category_code:
            cat = SubjectCategory.objects.filter(code=category_code, level='category').first()
            if cat:
                category_name = cat.name

        # 判断是否自设（带 Z/J/S 后缀）
        is_self_set = any(c in code for c in ['Z', 'J', 'S'])

        subject = SubjectCategory.objects.create(
            code=code,
            name=name_hint or f'未命名学科({code})',
            level=level,
            parent=parent,
            category_code=category_code,
            category_name=category_name,
            is_academic=is_academic,
            is_self_set=is_self_set,
        )
        self.log(f'  ⚡ 自动创建学科: {code} {subject.name}', 'info')
        return subject
    # ============== 学校 ==============

    def save_school(self, data):
        """
        保存或更新学校
        data keys: name(必), province_name, platform_id, code,
                   is_985, is_211, is_double_first, is_self_scoring,
                   school_type, province_area, ...
        """
        name = data.get('name')
        if not name:
            self.stats['schools']['skipped'] += 1
            return None

        province = None
        province_name = data.get('province_name')
        if province_name:
            province, _ = Province.objects.get_or_create(name=province_name)

        defaults = {k: v for k, v in {
            'province': province,
            'platform_id': data.get('platform_id'),
            'is_985': data.get('is_985', False),
            'is_211': data.get('is_211', False),
            'is_double_first': data.get('is_double_first', False),
            'is_self_scoring': data.get('is_self_scoring', False),
            'school_type': data.get('school_type', ''),
            'province_area': data.get('province_area', ''),
            'level': data.get('level', 'normal'),
        }.items() if v is not None}

        # 国标代码（可空，先用平台ID找学校，再考虑update code）
        code = data.get('code')

        try:
            # 优先按 platform_id 找
            if data.get('platform_id'):
                school = School.objects.filter(platform_id=data['platform_id']).first()
                if school:
                    for k, v in defaults.items():
                        setattr(school, k, v)
                    if code and not school.code:
                        school.code = code
                    school.save()
                    self.stats['schools']['updated'] += 1
                    return school

            # 按名字
            school, created = School.objects.update_or_create(
                name=name,
                defaults={**defaults, **({'code': code} if code else {})}
            )
            if created:
                self.stats['schools']['new'] += 1
                self.log(f'新增学校: {school.name}')
            else:
                self.stats['schools']['updated'] += 1
            return school
        except Exception as e:
            self.log(f'保存学校失败 {name}: {e}', 'error')
            self.stats['schools']['skipped'] += 1
            return None

    # ============== 学院 ==============

    def save_college(self, school, data):
        """
        data keys: name(必), platform_id, code, url
        """
        name = data.get('name')
        if not school or not name:
            self.stats['colleges']['skipped'] += 1
            return None

        try:
            # 优先按 platform_id 匹配
            if data.get('platform_id'):
                college = College.objects.filter(
                    school=school, platform_id=data['platform_id']
                ).first()
                if college:
                    if college.name != name:
                        college.name = name
                        college.save()
                    self.stats['colleges']['updated'] += 1
                    return college

            college, created = College.objects.update_or_create(
                school=school, name=name,
                defaults={
                    'platform_id': data.get('platform_id'),
                    'code': data.get('code', ''),
                    'url': data.get('url', ''),
                }
            )
            if created:
                self.stats['colleges']['new'] += 1
            else:
                self.stats['colleges']['updated'] += 1
            return college
        except Exception as e:
            self.log(f'保存学院失败 {name}: {e}', 'error')
            self.stats['colleges']['skipped'] += 1
            return None

    # ============== 专业 ==============

    def save_major(self, college, data):
        """
        data keys: code(必), name(必), degree_type, learning_type,
                   subject_category_code, platform_id, ...
        """
        code = data.get('code')
        name = data.get('name')
        if not college or not code or not name:
            self.stats['majors']['skipped'] += 1
            return None

        # 兜底找学科分类
        subject_category = None
        sc_code = data.get('subject_category_code')
        if sc_code:
            subject_category = self._get_or_create_subject(
                sc_code,
                name_hint=data.get('subject_category_name')
            )

        learning_type = data.get('learning_type', 'full_time')

        try:
            major, created = Major.objects.update_or_create(
                college=college,
                code=code,
                name=name,
                learning_type=learning_type,
                defaults={
                    'degree_type': data.get('degree_type', 'academic'),
                    'exam_type': data.get('exam_type', 'unified'),
                    'doctoral_point': data.get('doctoral_point', ''),
                    'platform_id': data.get('platform_id'),
                    'subject_category': subject_category,
                }
            )
            if created:
                self.stats['majors']['new'] += 1
            else:
                self.stats['majors']['updated'] += 1
            return major
        except Exception as e:
            self.log(f'保存专业失败 {name}({code}): {e}', 'error')
            self.stats['majors']['skipped'] += 1
            return None

    # ============== 研究方向 ==============

    def save_research_direction(self, major, data):
        """
        data keys: year(必), direction_name(必),
                   direction_code, raw_text, recruit_number,
                   is_direction_based, exam_subjects, note
        """
        year = data.get('year')
        direction_name = data.get('direction_name')
        if not major or not year or not direction_name:
            self.stats['research_directions']['skipped'] += 1
            return None

        try:
            obj, created = ResearchDirection.objects.update_or_create(
                major=major,
                year=year,
                direction_name=direction_name,
                defaults={
                    'direction_code': data.get('direction_code', ''),
                    'raw_text': data.get('raw_text', ''),
                    'recruit_number': data.get('recruit_number'),
                    'is_direction_based': data.get('is_direction_based', False),
                    'exam_subjects': data.get('exam_subjects', ''),
                    'note': data.get('note', ''),
                }
            )
            if created:
                self.stats['research_directions']['new'] += 1
            else:
                self.stats['research_directions']['updated'] += 1
            return obj
        except Exception as e:
            self.log(f'保存研究方向失败: {e}', 'error')
            self.stats['research_directions']['skipped'] += 1
            return None

    # ============== 分数线 ==============

    def save_score_line(self, data):
        """
        data keys:
            score_type(必): 'subject' | 'major'
            school_id(必): School.id 或 platform_id
            year(必)
            total_score(必)
            subject_category_code: 学科线时填
            major_id: 专业线时填
            politics_score, english_score,
            subject_one_score, subject_one_name,
            subject_two_score, subject_two_name,
            diff_total, diff_politics, diff_english,
            diff_subject_one, diff_subject_two,
            source_url, note
        """
        score_type = data.get('score_type')
        year = data.get('year')
        total_score = data.get('total_score')

        if score_type not in ('subject', 'major') or not year or total_score is None:
            self.stats['score_lines']['skipped'] += 1
            return None

        # 找学校
        school = data.get('school_obj')  # 优先用对象
        if not school:
            school = School.objects.filter(id=data.get('school_id')).first()
        if not school:
            self.log(f'分数线跳过：找不到学校', 'warning')
            self.stats['score_lines']['skipped'] += 1
            return None

        subject_category = None
        major = None

        if score_type == 'subject':
            sc_code = data.get('subject_category_code')
            if sc_code:
                subject_category = self._get_or_create_subject(
                    sc_code,
                    name_hint=data.get('subject_category_name')
                )
            if not subject_category:
                self.log(f'学科线跳过：找不到学科 {sc_code}', 'warning')
                self.stats['score_lines']['skipped'] += 1
                return None
            lookup = {'school': school, 'subject_category': subject_category, 'year': year, 'score_type': 'subject'}
        else:
            major = data.get('major_obj')
            if not major:
                major = Major.objects.filter(id=data.get('major_id')).first()
            if not major:
                self.log(f'专业线跳过：找不到专业', 'warning')
                self.stats['score_lines']['skipped'] += 1
                return None
            lookup = {'school': school, 'major': major, 'year': year, 'score_type': 'major'}

        defaults = {
            'total_score': total_score,
            'politics_score': data.get('politics_score'),
            'english_score': data.get('english_score'),
            'subject_one_score': data.get('subject_one_score'),
            'subject_one_name': data.get('subject_one_name', ''),
            'subject_two_score': data.get('subject_two_score'),
            'subject_two_name': data.get('subject_two_name', ''),
            'diff_total': data.get('diff_total'),
            'diff_politics': data.get('diff_politics'),
            'diff_english': data.get('diff_english'),
            'diff_subject_one': data.get('diff_subject_one'),
            'diff_subject_two': data.get('diff_subject_two'),
            'source_url': data.get('source_url', ''),
            'note': data.get('note', ''),
            'subject_category': subject_category,
            'major': major,
        }

        try:
            obj, created = ScoreLine.objects.update_or_create(
                **lookup,
                defaults=defaults
            )
            if created:
                self.stats['score_lines']['new'] += 1
            else:
                self.stats['score_lines']['updated'] += 1
            return obj
        except Exception as e:
            self.log(f'保存分数线失败: {e}', 'error')
            self.stats['score_lines']['skipped'] += 1
            return None

    # ============== 招生计划 ==============

    def save_enrollment(self, major, data):
        """
        data keys: year(必), plan_total, plan_exam, plan_recommend,
                   actual_total, ..., enroll_ratio, avg_score, ...
        """
        year = data.get('year')
        if not major or not year:
            self.stats['enrollments']['skipped'] += 1
            return None

        defaults = {k: v for k, v in {
            'plan_total': data.get('plan_total'),
            'plan_exam': data.get('plan_exam'),
            'plan_recommend': data.get('plan_recommend'),
            'actual_total': data.get('actual_total'),
            'actual_exam': data.get('actual_exam'),
            'actual_recommend': data.get('actual_recommend'),
            'apply_count': data.get('apply_count'),
            'enroll_ratio': data.get('enroll_ratio'),
            'avg_score': data.get('avg_score'),
            'min_score': data.get('min_score'),
            'max_score': data.get('max_score'),
            'plan_id': data.get('plan_id'),
            'source_url': data.get('source_url', ''),
            'note': data.get('note', ''),
        }.items() if v is not None or k in ('source_url', 'note')}

        try:
            obj, created = Enrollment.objects.update_or_create(
                major=major, year=year,
                defaults=defaults
            )
            if created:
                self.stats['enrollments']['new'] += 1
            else:
                self.stats['enrollments']['updated'] += 1
            return obj
        except Exception as e:
            self.log(f'保存招生失败: {e}', 'error')
            self.stats['enrollments']['skipped'] += 1
            return None

    # ============== 参考书 ==============

    def save_reference_book(self, major, data):
        """
        data keys: book_name(必), year, author, publisher,
                   edition, exam_subject, raw_text
        """
        book_name = data.get('book_name')
        if not major or not book_name:
            self.stats['reference_books']['skipped'] += 1
            return None

        try:
            obj, created = ReferenceBook.objects.update_or_create(
                major=major,
                book_name=book_name,
                year=data.get('year'),
                defaults={
                    'author': data.get('author', ''),
                    'publisher': data.get('publisher', ''),
                    'edition': data.get('edition', ''),
                    'exam_subject': data.get('exam_subject', ''),
                    'raw_text': data.get('raw_text', ''),
                }
            )
            if created:
                self.stats['reference_books']['new'] += 1
            else:
                self.stats['reference_books']['updated'] += 1
            return obj
        except Exception as e:
            self.log(f'保存参考书失败: {e}', 'error')
            self.stats['reference_books']['skipped'] += 1
            return None

    # ============== 学科评级 ==============

    def save_subject_rating(self, school, data):
        """
        data keys: subject_code(必), rating(必),
                   evaluation_round(默认round_4), year, source_url
        """
        subject_code = data.get('subject_code')
        rating = data.get('rating')
        if not school or not subject_code or not rating:
            self.stats['subject_ratings']['skipped'] += 1
            return None

        # 兜底：找不到学科自动创建
        subject = self._get_or_create_subject(subject_code, name_hint=data.get('subject_name'))
        if not subject:
            self.stats['subject_ratings']['skipped'] += 1
            return None

        evaluation_round = data.get('evaluation_round', 'round_4')

        try:
            obj, created = SubjectRating.objects.update_or_create(
                school=school,
                subject=subject,
                evaluation_round=evaluation_round,
                defaults={
                    'rating': rating,
                    'year': data.get('year'),
                    'source_url': data.get('source_url', ''),
                }
            )
            if created:
                self.stats['subject_ratings']['new'] += 1
            else:
                self.stats['subject_ratings']['updated'] += 1
            return obj
        except Exception as e:
            self.log(f'保存评级失败: {e}', 'error')
            self.stats['subject_ratings']['skipped'] += 1
            return None

    # ============== 统计输出 ==============

    def print_stats(self):
        print('\n' + '=' * 50)
        print('入库统计')
        print('=' * 50)
        for key, s in self.stats.items():
            total = s['new'] + s['updated'] + s['skipped']
            if total > 0:
                print(f'  {key:20s} 新增 {s["new"]:5d} | 更新 {s["updated"]:5d} | 跳过 {s["skipped"]:5d}')
        print('=' * 50 + '\n')