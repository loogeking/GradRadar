from django.db import models


class SubjectCategory(models.Model):
    """学科目录（国家统一）"""
    LEVEL_CHOICES = [
        ('first', '一级学科'),
        ('second', '二级学科'),
        ('professional', '专业学位类别'),
    ]

    code = models.CharField('学科代码', max_length=10, unique=True, db_index=True)
    name = models.CharField('学科名称', max_length=100)
    category = models.CharField('学科门类', max_length=50, blank=True,
                                help_text='如：工学、理学、文学等')
    level = models.CharField('层级', max_length=20, choices=LEVEL_CHOICES, default='first')
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='children',
        verbose_name='上级学科'
    )
    description = models.TextField('描述', blank=True)

    class Meta:
        verbose_name = '学科目录'
        verbose_name_plural = '学科目录'
        ordering = ['code']

    def __str__(self):
        return f'{self.code} {self.name}'


class SubjectRating(models.Model):
    """学科评级"""
    ROUND_CHOICES = [
        ('round_4', '第四轮学科评估'),
        ('round_5', '第五轮学科评估'),
    ]

    RATING_CHOICES = [
        ('A+', 'A+'), ('A', 'A'), ('A-', 'A-'),
        ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'),
        ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'),
    ]

    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='subject_ratings',
        verbose_name='所属学校'
    )
    subject = models.ForeignKey(
        SubjectCategory,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='学科'
    )
    rating = models.CharField('评级', max_length=5, choices=RATING_CHOICES)
    evaluation_round = models.CharField('评估轮次', max_length=20, choices=ROUND_CHOICES)
    year = models.IntegerField('评估年份', null=True, blank=True)
    source_url = models.URLField('数据来源', blank=True)
    note = models.TextField('备注', blank=True)

    class Meta:
        verbose_name = '学科评级'
        verbose_name_plural = '学科评级'
        ordering = ['subject', '-evaluation_round', 'rating']
        unique_together = [['school', 'subject', 'evaluation_round']]

    def __str__(self):
        return f'{self.school.name} - {self.subject.name} - {self.rating}'

    @property
    def rating_score(self):
        """评级转分数，方便排序（A+最高）"""
        score_map = {
            'A+': 9, 'A': 8, 'A-': 7,
            'B+': 6, 'B': 5, 'B-': 4,
            'C+': 3, 'C': 2, 'C-': 1,
        }
        return score_map.get(self.rating, 0)