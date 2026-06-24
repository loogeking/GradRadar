from django.db import models


class Province(models.Model):
    """省级行政区"""
    name = models.CharField('省份名称', max_length=50, unique=True)
    short_name = models.CharField('简称', max_length=10, blank=True)

    class Meta:
        verbose_name = '省份'
        verbose_name_plural = '省份'
        ordering = ['id']

    def __str__(self):
        return self.name


class School(models.Model):
    """高校"""

    LEVEL_CHOICES = [
        ('985', '985工程'),
        ('211', '211工程'),
        ('double_first', '双一流'),
        ('normal', '普通院校'),
    ]

    SCHOOL_TYPE_CHOICES = [
        ('comprehensive', '综合类'),
        ('science_eng', '理工类'),
        ('normal_edu', '师范类'),
        ('medical', '医药类'),
        ('finance', '财经类'),
        ('political_law', '政法类'),
        ('agriculture', '农林类'),
        ('ethnic', '民族类'),
        ('art', '艺术类'),
        ('military', '军事类'),
        ('language', '语言类'),
        ('sports', '体育类'),
        ('other', '其他'),
    ]

    PROVINCE_AREA_CHOICES = [
        ('A', 'A区'),
        ('B', 'B区'),
    ]

    # 基础信息
    name = models.CharField('学校名称', max_length=100, unique=True)
    code = models.CharField(
        '学校代码', max_length=10, unique=True,
        blank=True, null=True,
        help_text='国标代码，如 10003'
    )
    province = models.ForeignKey(
        Province,
        on_delete=models.PROTECT,
        related_name='schools',
        verbose_name='所在省份'
    )

    # 层次标签
    level = models.CharField(
        '院校层次', max_length=20,
        choices=LEVEL_CHOICES, default='normal'
    )
    is_985 = models.BooleanField('是否985', default=False)
    is_211 = models.BooleanField('是否211', default=False)
    is_double_first = models.BooleanField('是否双一流', default=False)

    # v2.0 新增字段
    platform_id = models.IntegerField(
        '采集平台ID', null=True, blank=True, db_index=True,
        help_text='数据采集源的内部ID，仅用于增量更新和数据校验'
    )
    province_area = models.CharField(
        '考研区域', max_length=2,
        choices=PROVINCE_AREA_CHOICES, blank=True,
        help_text='国家线A区/B区'
    )
    is_self_scoring = models.BooleanField(
        '是否自划线', default=False,
        help_text='34所自主划线高校之一'
    )
    school_type = models.CharField(
        '学校类型', max_length=20,
        choices=SCHOOL_TYPE_CHOICES, blank=True,
        help_text='综合/理工/师范等分类'
    )

    # 其他
    official_url = models.URLField('研究生院官网', blank=True)
    logo_url = models.URLField('校徽URL', blank=True)
    description = models.TextField('简介', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '院校'
        verbose_name_plural = '院校'
        ordering = ['code']

    def __str__(self):
        return self.name


class College(models.Model):
    """学院"""
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='colleges',
        verbose_name='所属学校'
    )
    name = models.CharField('学院名称', max_length=100)
    code = models.CharField('学院代码', max_length=10, blank=True)
    url = models.URLField('学院官网', blank=True)

    # v2.0 新增
    platform_id = models.IntegerField(
        '采集平台ID', null=True, blank=True, db_index=True,
        help_text='对应平台 depart_id'
    )

    class Meta:
        verbose_name = '学院'
        verbose_name_plural = '学院'
        ordering = ['school', 'name']
        unique_together = [['school', 'name']]

    def __str__(self):
        return f'{self.school.name} - {self.name}'