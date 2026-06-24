from django.db import models
from apps.schools.models import College


class Major(models.Model):
    """招生专业（专业实体，不区分年份）"""

    DEGREE_CHOICES = [
        ('academic', '学术学位'),
        ('professional', '专业学位'),
    ]

    LEARNING_TYPE_CHOICES = [
        ('full_time', '全日制'),
        ('part_time', '非全日制'),
        ('both', '全日制+非全日制'),
    ]

    EXAM_TYPE_CHOICES = [
        ('unified', '统考'),
        ('single', '单考'),
        ('joint', '联考'),
        ('management', '管理类联考'),
        ('recommend', '推免'),
        ('other', '其他'),
    ]

    DOCTORAL_POINT_CHOICES = [
        ('doctoral_first', '一级学科博士点'),
        ('doctoral_second', '二级学科博士点'),
        ('doctoral', '博士点'),
        ('master', '硕士点'),
        ('none', '无'),
    ]

    # 核心字段
    college = models.ForeignKey(
        College, on_delete=models.CASCADE,
        related_name='majors', verbose_name='所属学院'
    )
    code = models.CharField(
        '专业代码', max_length=10,
        help_text='如 081200、085404'
    )
    name = models.CharField('专业名称', max_length=100)
    degree_type = models.CharField(
        '学位类型', max_length=20,
        choices=DEGREE_CHOICES, default='academic'
    )

    # 关联学科目录
    subject_category = models.ForeignKey(
        'subjects.SubjectCategory',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='majors',
        verbose_name='所属学科',
        help_text='关联到一级学科或专业学位类别'
    )

    # v2.0 新增字段
    learning_type = models.CharField(
        '学习方式', max_length=20,
        choices=LEARNING_TYPE_CHOICES, default='full_time'
    )
    exam_type = models.CharField(
        '考试类型', max_length=20,
        choices=EXAM_TYPE_CHOICES, default='unified', blank=True
    )
    doctoral_point = models.CharField(
        '学位点情况', max_length=20,
        choices=DOCTORAL_POINT_CHOICES, blank=True
    )
    platform_id = models.IntegerField(
        '采集平台专业ID', null=True, blank=True, db_index=True,
        help_text='对应平台 spe_id'
    )

    class Meta:
        verbose_name = '专业'
        verbose_name_plural = '专业'
        ordering = ['college', 'code']
        unique_together = [['college', 'code', 'name', 'learning_type']]

    def __str__(self):
        return f'{self.college.school.name} - {self.name}({self.code})'


class ResearchDirection(models.Model):
    """研究方向（按年份）"""

    major = models.ForeignKey(
        Major,
        on_delete=models.CASCADE,
        related_name='research_directions',
        verbose_name='所属专业'
    )
    year = models.IntegerField('年份', db_index=True)

    # 方向标识
    direction_code = models.CharField(
        '方向代码', max_length=10, blank=True,
        help_text='如 01、02'
    )
    direction_name = models.CharField(
        '方向名称', max_length=200,
        help_text='清洗后的方向名'
    )
    raw_text = models.CharField(
        '原始文本', max_length=300, blank=True,
        help_text='接口返回的原始字符串'
    )

    # 招生信息
    recruit_number = models.IntegerField(
        '招生人数', null=True, blank=True
    )
    is_direction_based = models.BooleanField(
        '是否按方向独立统计', default=False,
        help_text='True=招生人数是该方向独立的；False=招生人数是专业总数'
    )

    # 考试科目
    exam_subjects = models.TextField(
        '初试考试科目', blank=True,
        help_text='保留原文本格式'
    )

    note = models.TextField('备注', blank=True)

    class Meta:
        verbose_name = '研究方向'
        verbose_name_plural = '研究方向'
        ordering = ['major', '-year', 'direction_code']
        unique_together = [['major', 'year', 'direction_name']]

    def __str__(self):
        return f'{self.major.name} {self.year}年 {self.direction_name}'


class ScoreLine(models.Model):
    """分数线（支持多层级：学科线/专业线）"""

    SCORE_TYPE_CHOICES = [
        ('subject', '学科线'),
        ('major', '专业线'),
    ]

    # 归属关系
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='score_lines',
        verbose_name='所属学校'
    )
    score_type = models.CharField(
        '分数线类型', max_length=20,
        choices=SCORE_TYPE_CHOICES, db_index=True
    )
    subject_category = models.ForeignKey(
        'subjects.SubjectCategory',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='score_lines',
        verbose_name='关联学科',
        help_text='学科线时填'
    )
    major = models.ForeignKey(
        Major,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='score_lines',
        verbose_name='关联专业',
        help_text='专业线时填'
    )

    year = models.IntegerField('年份', db_index=True)

    # 分数字段
    total_score = models.IntegerField('总分线')
    politics_score = models.IntegerField('政治', null=True, blank=True)
    english_score = models.IntegerField('英语', null=True, blank=True)
    subject_one_score = models.IntegerField(
        '业务课一分数', null=True, blank=True,
        help_text='可能是数学、管综、专业基础等'
    )
    subject_one_name = models.CharField(
        '业务课一科目', max_length=50, blank=True,
        help_text='如：数学一、199管综、临床综合'
    )
    subject_two_score = models.IntegerField(
        '业务课二分数', null=True, blank=True,
        help_text='为空表示不考'
    )
    subject_two_name = models.CharField(
        '业务课二科目', max_length=50, blank=True
    )

    # 与国家线差值
    diff_total = models.IntegerField(
        '总分高于国家线', null=True, blank=True,
        help_text='正数表示高于国家线，负数表示低于'
    )
    diff_politics = models.IntegerField('政治差值', null=True, blank=True)
    diff_english = models.IntegerField('英语差值', null=True, blank=True)
    diff_subject_one = models.IntegerField('业务课一差值', null=True, blank=True)
    diff_subject_two = models.IntegerField('业务课二差值', null=True, blank=True)

    # 元信息
    source_url = models.URLField('数据来源', blank=True)
    note = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '分数线'
        verbose_name_plural = '分数线'
        ordering = ['-year', 'school', 'score_type']
        constraints = [
            models.UniqueConstraint(
                fields=['school', 'subject_category', 'year'],
                condition=models.Q(score_type='subject'),
                name='unique_subject_score_line'
            ),
            models.UniqueConstraint(
                fields=['school', 'major', 'year'],
                condition=models.Q(score_type='major'),
                name='unique_major_score_line'
            ),
        ]

    def __str__(self):
        if self.score_type == 'subject' and self.subject_category:
            return f'{self.school.name} {self.subject_category.name} {self.year}年 {self.total_score}分'
        elif self.score_type == 'major' and self.major:
            return f'{self.major.name} {self.year}年 {self.total_score}分'
        return f'{self.school.name} {self.year}年 {self.total_score}分'

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.score_type == 'subject' and not self.subject_category:
            raise ValidationError('学科线必须关联学科目录')
        if self.score_type == 'major' and not self.major:
            raise ValidationError('专业线必须关联专业')


class Enrollment(models.Model):
    """招生与录取数据"""

    major = models.ForeignKey(
        Major,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='专业'
    )
    year = models.IntegerField('年份')

    # 计划数
    plan_total = models.IntegerField('计划招生总数', null=True, blank=True)
    plan_exam = models.IntegerField('统考计划数', null=True, blank=True)
    plan_recommend = models.IntegerField('推免计划数', null=True, blank=True)

    # 实际录取数
    actual_total = models.IntegerField('实际录取总数', null=True, blank=True)
    actual_exam = models.IntegerField('实际统考录取', null=True, blank=True)
    actual_recommend = models.IntegerField('实际推免录取', null=True, blank=True)

    # 报名数
    apply_count = models.IntegerField('报名人数', null=True, blank=True)

    # 派生指标
    enroll_ratio = models.FloatField(
        '报录比', null=True, blank=True,
        help_text='例如 8.5 表示 8.5:1'
    )
    avg_score = models.FloatField('录取平均分', null=True, blank=True)
    min_score = models.IntegerField('录取最低分', null=True, blank=True)
    max_score = models.IntegerField('录取最高分', null=True, blank=True)

    # 平台标识
    plan_id = models.IntegerField(
        '平台计划ID', null=True, blank=True, db_index=True,
        help_text='对应平台 plan_id，按年份变化'
    )

    # 元信息
    source_url = models.URLField('数据来源', blank=True)
    note = models.TextField('备注', blank=True)

    class Meta:
        verbose_name = '招生计划'
        verbose_name_plural = '招生计划'
        ordering = ['-year', 'major']
        unique_together = [['major', 'year']]

    def __str__(self):
        return f'{self.major.name} {self.year}年'

    @property
    def recommend_ratio(self):
        """推免比例"""
        if self.plan_total and self.plan_recommend:
            return round(self.plan_recommend / self.plan_total * 100, 2)
        return None

    @property
    def computed_enroll_ratio(self):
        """报录比"""
        if self.enroll_ratio:
            return self.enroll_ratio
        if self.apply_count and self.actual_total:
            return round(self.apply_count / self.actual_total, 2)
        return None


class ReferenceBook(models.Model):
    """参考书目"""

    major = models.ForeignKey(
        Major,
        on_delete=models.CASCADE,
        related_name='reference_books',
        verbose_name='专业'
    )
    year = models.IntegerField(
        '适用年份', null=True, blank=True, db_index=True,
        help_text='参考书目适用的考试年份'
    )

    book_name = models.CharField('书名', max_length=200)
    author = models.CharField('作者', max_length=100, blank=True)
    publisher = models.CharField('出版社', max_length=100, blank=True)
    edition = models.CharField('版本', max_length=50, blank=True)
    exam_subject = models.CharField('对应考试科目', max_length=100, blank=True)

    raw_text = models.TextField(
        '原始书目文本', blank=True,
        help_text='接口返回的整段书目原文，用于兜底展示'
    )

    class Meta:
        verbose_name = '参考书目'
        verbose_name_plural = '参考书目'
        ordering = ['major', '-year', 'book_name']

    def __str__(self):
        return f'{self.book_name} - {self.author}'


class NationalScoreLine(models.Model):
    """国家线"""

    AREA_CHOICES = [
        ('A', 'A区'),
        ('B', 'B区'),
    ]

    year = models.IntegerField('年份', db_index=True)
    area = models.CharField('区域', max_length=2, choices=AREA_CHOICES)
    subject_category = models.ForeignKey(
        'subjects.SubjectCategory',
        on_delete=models.CASCADE,
        related_name='national_score_lines',
        verbose_name='学科门类',
        help_text='应关联到门类层级（如01哲学、08工学）'
    )

    total_score = models.IntegerField('总分线')
    politics_score = models.IntegerField('政治', null=True, blank=True)
    english_score = models.IntegerField('英语', null=True, blank=True)
    subject_one_score = models.IntegerField('业务课一', null=True, blank=True)
    subject_two_score = models.IntegerField('业务课二', null=True, blank=True)

    source_url = models.URLField('数据来源', blank=True)
    note = models.TextField('备注', blank=True)

    class Meta:
        verbose_name = '国家线'
        verbose_name_plural = '国家线'
        ordering = ['-year', 'area', 'subject_category']
        unique_together = [['year', 'area', 'subject_category']]

    def __str__(self):
        return f'{self.year}年 {self.area}区 {self.subject_category.name} {self.total_score}分'