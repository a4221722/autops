from django.db import models

# Create your models here.
class ora_awr_report(models.Model):
    cluster_name = models.CharField('实例名称',max_length=50)
    end_snap_id = models.IntegerField('截止快照id')
    interval = models.CharField('时间区间',max_length=30)
    create_time = models.DateTimeField('创建时间',auto_now_add=True)
    awr_location = models.CharField('awr报告',max_length=200)
    status = models.CharField('状态',default='init',max_length=500)

    class Meta:
        unique_together = (("cluster_name","end_snap_id"),)
        verbose_name = u'awr报告'
        verbose_name_plural = u'awr报告'
