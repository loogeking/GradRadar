from django.db import models
from apps.schools.models import College


class Tutor(models.Model):
    """导师"""
    TITLE_CHOICES = [
        ('professor', '教授'),
        ('associate', '副教授'),
        ('lecturer', '讲师'),
        ('assistant', '助理教授'),
        ('other', '其他'),
    ]

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='tutors',
        verbose_name='所属学院'
    )
    name = models.CharField('姓名', max_length=50)
    title = models.CharField('职称', max_length=20, choices=TITLE_CHOICES, default='other')
    research_area = models.TextField('研究方向', blank=True)
    email = models.EmailField('邮箱', blank=True)
    homepage = models.URLField('个人主页', blank=True)
    is_doctoral_supervisor = models.BooleanField('是否博导', default=False)
    bio = models.TextField('简介', blank=True)

    class Meta:
        verbose_name = '导师'
        verbose_name_plural = '导师'
        ordering = ['college', 'name']

    def __str__(self):
        return f'{self.name}({self.college.name})'