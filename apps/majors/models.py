from django.db import models
from apps.schools.models import College


class Major(models.Model):
    """专业"""
    DEGREE_CHOICES = [
        ('academic', '学术学位'),
        ('professional', '专业学位'),
    ]

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='majors',
        verbose_name='所属学院'
    )
    code = models.CharField('专业代码', max_length=10)
    name = models.CharField('专业名称', max_length=100)
    degree_type = models.CharField('学位类型', max_length=20, choices=DEGREE_CHOICES, default='academic')
    research_direction = models.TextField('研究方向', blank=True)
    exam_subjects = models.TextField('考试科目', blank=True, help_text='初试科目，逗号分隔')
    subject_category = models.ForeignKey(
        'subjects.SubjectCategory',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='majors',
        verbose_name='学科目录'
    )

    class Meta:
        verbose_name = '专业'
        verbose_name_plural = '专业'
        ordering = ['college', 'code']
        unique_together = [['college', 'code', 'name']]

    def __str__(self):
        return f'{self.college.school.name} - {self.name}({self.code})'


class ScoreLine(models.Model):
    """复试分数线"""
    major = models.ForeignKey(
        Major,
        on_delete=models.CASCADE,
        related_name='score_lines',
        verbose_name='专业'
    )
    year = models.IntegerField('年份')
    total_score = models.IntegerField('总分线')
    politics = models.IntegerField('政治线', null=True, blank=True)
    english = models.IntegerField('英语线', null=True, blank=True)
    math = models.IntegerField('数学线', null=True, blank=True)
    professional = models.IntegerField('专业课线', null=True, blank=True)
    source_url = models.URLField('数据来源', blank=True)
    note = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '复试分数线'
        verbose_name_plural = '复试分数线'
        ordering = ['-year', 'major']
        unique_together = [['major', 'year']]

    def __str__(self):
        return f'{self.major.name} {self.year}年 {self.total_score}分'


class Enrollment(models.Model):
    """招生计划"""
    major = models.ForeignKey(
        Major,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='专业'
    )
    year = models.IntegerField('年份')
    plan_total = models.IntegerField('计划招生总数', null=True, blank=True)
    plan_exam = models.IntegerField('统考招生数', null=True, blank=True)
    plan_recommend = models.IntegerField('推免招生数', null=True, blank=True)
    actual_total = models.IntegerField('实际录取总数', null=True, blank=True)
    apply_count = models.IntegerField('报名人数', null=True, blank=True)
    source_url = models.URLField('数据来源', blank=True)
    note = models.TextField('备注', blank=True)

    class Meta:
        verbose_name = '招生计划'
        verbose_name_plural = '招生计划'
        ordering = ['-year', 'major']
        unique_together = [['major', 'year']]

    def __str__(self):
        return f'{self.major.name} {self.year}年 计划{self.plan_total}人'

    @property
    def recommend_ratio(self):
        """推免比例"""
        if self.plan_total and self.plan_recommend:
            return round(self.plan_recommend / self.plan_total * 100, 2)
        return None


class ReferenceBook(models.Model):
    """参考书目"""
    major = models.ForeignKey(
        Major,
        on_delete=models.CASCADE,
        related_name='reference_books',
        verbose_name='专业'
    )
    book_name = models.CharField('书名', max_length=200)
    author = models.CharField('作者', max_length=100, blank=True)
    publisher = models.CharField('出版社', max_length=100, blank=True)
    edition = models.CharField('版本', max_length=50, blank=True)
    exam_subject = models.CharField('对应考试科目', max_length=100, blank=True)

    class Meta:
        verbose_name = '参考书目'
        verbose_name_plural = '参考书目'
        ordering = ['major', 'book_name']

    def __str__(self):
        return f'{self.book_name} - {self.author}'