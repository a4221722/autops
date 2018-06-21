from django.db import models
from sql.aes_decryptor import Prpcrypt

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

class os_host_config(models.Model):
    host_name = models.CharField('主机名称',max_length=50,unique=True)
    host_ip = models.CharField('主机地址',max_length=200,unique=True)
    host_port = models.IntegerField('主机ssh端口',default=22)
    host_user = models.CharField('主机用户名',max_length=100)
    host_password = models.CharField('主机密码',max_length=100)
    create_time = models.DateTimeField('创建时间',auto_now_add=True)
    update_time = models.DateTimeField('更新时间',auto_now=True)
    snap_flag = models.IntegerField('快照标志位',default=0)

    class Meta:
        verbose_name = u'主机信息'
        verbose_name_plural = u'主机信息'

    def save(self, *args, **kwargs):
        if not kwargs.get('keepPass'):
            pc = Prpcrypt() #初始化
            self.host_password = pc.encrypt(self.host_password)
        else:
            kwargs.pop('keepPass')
        super(os_host_config,self).save(*args, **kwargs)
