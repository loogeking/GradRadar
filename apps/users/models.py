from django.db import models
from django.contrib.auth.models import User
from apps.schools.models import School
from apps.majors.models import Major


class Favorite(models.Model):
    """用户收藏"""
    TARGET_CHOICES = [
        ('school', '院校'),
        ('major', '专业'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='用户'
    )
    target_type = models.CharField('收藏类型', max_length=10, choices=TARGET_CHOICES)
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='favorited_by',
        verbose_name='收藏的学校'
    )
    major = models.ForeignKey(
        Major,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='favorited_by',
        verbose_name='收藏的专业'
    )
    note = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('收藏时间', auto_now_add=True)

    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = '收藏'
        ordering = ['-created_at']

    def __str__(self):
        target = self.school if self.target_type == 'school' else self.major
        return f'{self.user.username} 收藏了 {target}'