# -*- coding: UTF-8 -*- 
from django.db import models
from django.contrib.auth.models import AbstractUser
from .aes_decryptor import Prpcrypt
import datetime
from .const import Const

# Create your models here.

#角色分两种：
#1.工程师：可以提交SQL上线单的工程师们，username字段为登录用户名，display字段为展示的中文名。
#2.审核人：可以审核并执行SQL上线单的管理者、高级工程师、系统管理员们。
class users(AbstractUser):
    display = models.CharField('显示的中文名', max_length=50)
    role = models.CharField('角色', max_length=20, choices=(('工程师','工程师'),('审核人','审核人'),('其他','其他')), default='其他')
    is_ldapuser = models.BooleanField('ldap用戶', default=False)
    wechat_account = models.CharField('企业微信名', max_length=50,null=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = u'用户基本信息配置'
        verbose_name_plural = u'用户基本信息配置'
users._meta.get_field('is_active').default = False # ldap default can't login, need admin to control


#线上oracle地址:
class ora_primary_config(models.Model):
    cluster_name = models.CharField('实例名称',max_length=50,unique=True)
    primary_host = models.CharField('主库地址',max_length=200)
    primary_port = models.IntegerField('主库端口',default=1521)
    primary_srv = models.CharField('主库service name',max_length=100)
    primary_user = models.CharField('主库用户名',max_length=100)
    primary_password = models.CharField('主库密码',max_length=100)
    standby_host = models.CharField('备库地址',max_length=200)
    standby_port = models.IntegerField('备库端口',default=1521)
    standby_srv = models.CharField('备库service name',max_length=100)
    charset = models.CharField('字符集',max_length=100,default='gbk',choices=(('gbk','gbk'),('utf8','utf8')))
    create_time = models.DateTimeField('创建时间',auto_now_add=True)
    update_time = models.DateTimeField('更新时间',auto_now=True)
    dict_time = models.DateTimeField('更新数据字典时间',default = datetime.datetime.fromtimestamp(0))#time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(0)))

    def __str__(self):
        return self.cluster_name
    class Meta:
        verbose_name = u'Oracle数据库信息'
        verbose_name_plural = u'Oracle数据库信息'

    def save(self, *args, **kwargs):
        if not kwargs.get('keepPass'):
            pc = Prpcrypt() #初始化
            self.primary_password = pc.encrypt(self.primary_password)
        else:
            kwargs.pop('keepPass')
        super(ora_primary_config,self).save(*args, **kwargs)


#存放各个SQL上线工单的详细内容，可定期归档或清理历史数据，也可通过alter table workflow row_format=compressed; 来进行压缩
class workflow(models.Model):
    workflow_name = models.CharField('工单内容', max_length=50)
    engineer = models.CharField('发起人', max_length=50)
    review_man = models.CharField('审核人', max_length=50)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    finish_time = models.DateTimeField('结束时间', null=True, blank=True)
    status = models.CharField(max_length=50, choices=tuple([(v,v) for k,v in Const.workflowStatus.items()]))#(('已正常结束','已正常结束'),('人工终止流程','人工终止流程'),('自动审核中','自动审核中'),('等待审核人审核','等待审核人审核'),('执行中','执行中'),('自动审核不通过','自动审核不通过'),('执行有异常','执行有异常')))
    #is_backup = models.IntegerField('是否备份，0为否，1为是', choices=((0,0),(1,1)))
    is_backup = models.CharField('是否备份', choices=(('否','否'),('是','是')), max_length=20)
    review_content = models.TextField('自动审核内容的JSON格式')
    cluster_name = models.CharField('集群名称', max_length=500)     #master_config表的cluster_name列的外键
    reviewok_time = models.DateTimeField('人工审核通过的时间', null=True, blank=True)
    sql_content = models.TextField('具体sql内容')
    execute_result = models.TextField('执行结果的JSON格式')
    message = models.TextField('备注说明',null=True)
    data_change_type = models.CharField('数据变更类型',choices=(('数据修订','数据修订'),('数据初始化','数据初始化'),('数据迁移','数据迁移')),max_length=50)
    reason = models.CharField('原因',max_length=200)
    operator = models.CharField('处理人', max_length=50,null=True)

    def __str__(self):
        return self.workflow_name
    class Meta:
        verbose_name = u'工单管理'
        verbose_name_plural = u'工单管理'

#储存所有的表名
class ora_tables(models.Model):
    instance_id = models.IntegerField('实例id', null=False)
    schema_name = models.CharField('schema名', max_length=40,null=False)
    table = models.CharField('表名', max_length=40,null=False) #格式为schema.table
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return self.cluster_name+'.'+self.table
    class Meta:
        unique_together = (("instance_id","schema_name","table"),)
        verbose_name = u'表数据字典'
        verbose_name_plural = u'表数据字典'

#用户dml和select表的权限
class ora_tab_privs(models.Model):
    username = models.CharField('用户名',max_length=40,null=False)
    table = models.ForeignKey(ora_tables)

    class Meta:
        unique_together = (("username","table"),)
        verbose_name = u'用户表级权限管理'
        verbose_name_plural = u'用户表级权限管理'

#操作控制表
class operation_ctl(models.Model):
    data_type = models.CharField('数据类型',max_length=40,null=False)
    opt_type = models.CharField('操作类型',max_length=40,null=False)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    modify_time = models.DateTimeField('修改时间', auto_now=True)
    status = models.CharField('状态',max_length=40,null=False,choices=(('进行中','进行中'),('正常','正常')))
    class Meta:
        unique_together = (("data_type","opt_type"),)
        verbose_name = u'用户表级权限管理'
        verbose_name_plural = u'用户表级权限管理'

#操作记录表
class operation_record(models.Model):
    data_type = models.CharField('数据类型',max_length=40,null=False)
    opt_type = models.CharField('操作类型',max_length=40,null=False)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    modify_time = models.DateTimeField('修改时间', auto_now=True)
    finish_time = models.DateTimeField('结束时间',null=True)
    status = models.CharField('状态',max_length=40,null=False,choices=(('已结束','已结束'),('进行中','进行中'),('有异常','有异常'),('正常','正常')))
    message = models.TextField('信息')
    class Meta:
        verbose_name = u'操作记录表'
        verbose_name_plural = u'操作记录表'
