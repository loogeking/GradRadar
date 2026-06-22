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

    name = models.CharField('学校名称', max_length=100, unique=True)
    code = models.CharField('学校代码', max_length=10, unique=True, blank=True, null=True)
    province = models.ForeignKey(
        Province,
        on_delete=models.PROTECT,
        related_name='schools',
        verbose_name='所在省份'
    )
    level = models.CharField('院校层次', max_length=20, choices=LEVEL_CHOICES, default='normal')
    is_985 = models.BooleanField('是否985', default=False)
    is_211 = models.BooleanField('是否211', default=False)
    is_double_first = models.BooleanField('是否双一流', default=False)
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

    class Meta:
        verbose_name = '学院'
        verbose_name_plural = '学院'
        ordering = ['school', 'name']
        unique_together = [['school', 'name']]

    def __str__(self):
        return f'{self.school.name} - {self.name}'