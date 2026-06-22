from django.db import models
from apps.schools.models import School, College


class Notice(models.Model):
    """通知公告"""
    TYPE_CHOICES = [
        ('admission', '招生简章'),
        ('score_line', '复试分数线'),
        ('retest', '复试通知'),
        ('adjustment', '调剂公告'),
        ('admit_list', '拟录取名单'),
        ('other', '其他'),
    ]

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='notices',
        verbose_name='所属学校'
    )
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='notices',
        verbose_name='所属学院',
        null=True,
        blank=True
    )
    title = models.CharField('公告标题', max_length=300)
    url = models.URLField('公告链接', max_length=500)
    publish_date = models.DateField('发布日期', null=True, blank=True)
    notice_type = models.CharField('公告类型', max_length=20, choices=TYPE_CHOICES, default='other')
    content_summary = models.TextField('内容摘要', blank=True)
    created_at = models.DateTimeField('采集时间', auto_now_add=True)

    class Meta:
        verbose_name = '公告'
        verbose_name_plural = '公告'
        ordering = ['-publish_date', '-created_at']

    def __str__(self):
        return self.title