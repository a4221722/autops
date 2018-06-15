# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.auth.models
import django.core.validators
import django.utils.timezone
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='users',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', blank=True, null=True)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('username', models.CharField(verbose_name='username', max_length=30, unique=True, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], error_messages={'unique': 'A user with that username already exists.'})),
                ('first_name', models.CharField(verbose_name='first name', max_length=30, blank=True)),
                ('last_name', models.CharField(verbose_name='last name', max_length=30, blank=True)),
                ('email', models.EmailField(verbose_name='email address', max_length=254, blank=True)),
                ('is_staff', models.BooleanField(verbose_name='staff status', default=False, help_text='Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(verbose_name='active', default=False, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('date_joined', models.DateTimeField(verbose_name='date joined', default=django.utils.timezone.now)),
                ('display', models.CharField(verbose_name='显示的中文名', max_length=50)),
                ('role', models.CharField(verbose_name='角色', max_length=20, default='其他', choices=[('工程师', '工程师'), ('审核人', '审核人'), ('其他', '其他')])),
                ('is_ldapuser', models.BooleanField(verbose_name='ldap用戶', default=False)),
                ('groups', models.ManyToManyField(verbose_name='groups', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group')),
                ('user_permissions', models.ManyToManyField(verbose_name='user permissions', blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission')),
            ],
            options={
                'verbose_name': '用户基本信息配置',
                'verbose_name_plural': '用户基本信息配置',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='operation_ctl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('data_type', models.CharField(verbose_name='数据类型', max_length=40)),
                ('opt_type', models.CharField(verbose_name='操作类型', max_length=40)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('modify_time', models.DateTimeField(verbose_name='修改时间', auto_now=True)),
                ('status', models.CharField(verbose_name='状态', max_length=40, choices=[('进行中', '进行中'), ('正常', '正常')])),
            ],
            options={
                'verbose_name': '用户表级权限管理',
                'verbose_name_plural': '用户表级权限管理',
            },
        ),
        migrations.CreateModel(
            name='operation_record',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('data_type', models.CharField(verbose_name='数据类型', max_length=40)),
                ('opt_type', models.CharField(verbose_name='操作类型', max_length=40)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('modify_time', models.DateTimeField(verbose_name='修改时间', auto_now=True)),
                ('finish_time', models.DateTimeField(verbose_name='结束时间', null=True)),
                ('status', models.CharField(verbose_name='状态', max_length=40, choices=[('已结束', '已结束'), ('进行中', '进行中'), ('有异常', '有异常'), ('正常', '正常')])),
                ('message', models.TextField(verbose_name='信息')),
            ],
            options={
                'verbose_name': '操作记录表',
                'verbose_name_plural': '操作记录表',
            },
        ),
        migrations.CreateModel(
            name='ora_primary_config',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('cluster_name', models.CharField(verbose_name='集群名称', max_length=50, unique=True)),
                ('primary_host', models.CharField(verbose_name='主库地址', max_length=200)),
                ('primary_port', models.IntegerField(verbose_name='主库端口', default=1521)),
                ('primary_srv', models.CharField(verbose_name='主库service name', max_length=100)),
                ('primary_user', models.CharField(verbose_name='主库用户名', max_length=100)),
                ('primary_password', models.CharField(verbose_name='主库密码', max_length=100)),
                ('standby_host', models.CharField(verbose_name='备库地址', max_length=200)),
                ('standby_port', models.IntegerField(verbose_name='备库端口', default=1521)),
                ('standby_srv', models.CharField(verbose_name='备库service name', max_length=100)),
                ('charset', models.CharField(verbose_name='字符集', max_length=100, default='gbk', choices=[('gbk', 'gbk'), ('utf8', 'utf8')])),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
                ('dict_time', models.DateTimeField(verbose_name='更新数据字典时间', default=datetime.datetime(1970, 1, 1, 8, 0))),
            ],
            options={
                'verbose_name': 'Oracle数据库信息',
                'verbose_name_plural': 'Oracle数据库信息',
            },
        ),
        migrations.CreateModel(
            name='ora_tab_privs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('username', models.CharField(verbose_name='用户名', max_length=40)),
            ],
            options={
                'verbose_name': '用户表级权限管理',
                'verbose_name_plural': '用户表级权限管理',
            },
        ),
        migrations.CreateModel(
            name='ora_tables',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('cluster_name', models.CharField(verbose_name='表名', max_length=60)),
                ('schema_name', models.CharField(verbose_name='schema名', max_length=40)),
                ('table', models.CharField(verbose_name='表名', max_length=40)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
            ],
            options={
                'verbose_name': '表数据字典',
                'verbose_name_plural': '表数据字典',
            },
        ),
        migrations.CreateModel(
            name='workflow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('workflow_name', models.CharField(verbose_name='工单内容', max_length=50)),
                ('engineer', models.CharField(verbose_name='发起人', max_length=50)),
                ('review_man', models.CharField(verbose_name='审核人', max_length=50)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('finish_time', models.DateTimeField(verbose_name='结束时间', blank=True, null=True)),
                ('status', models.CharField(max_length=50, choices=[('已正常结束', '已正常结束'), ('人工终止流程', '人工终止流程'), ('自动审核中', '自动审核中'), ('等待审核人审核', '等待审核人审核'), ('执行中', '执行中'), ('自动审核不通过', '自动审核不通过'), ('执行有异常', '执行有异常')])),
                ('is_backup', models.CharField(verbose_name='是否备份', max_length=20, choices=[('否', '否'), ('是', '是')])),
                ('review_content', models.TextField(verbose_name='自动审核内容的JSON格式')),
                ('cluster_name', models.CharField(verbose_name='集群名称', max_length=50)),
                ('reviewok_time', models.DateTimeField(verbose_name='人工审核通过的时间', blank=True, null=True)),
                ('sql_content', models.TextField(verbose_name='具体sql内容')),
                ('execute_result', models.TextField(verbose_name='执行结果的JSON格式')),
                ('messgae', models.TextField(verbose_name='备注说明')),
            ],
            options={
                'verbose_name': '工单管理',
                'verbose_name_plural': '工单管理',
            },
        ),
        migrations.AlterUniqueTogether(
            name='ora_tables',
            unique_together=set([('cluster_name', 'schema_name', 'table')]),
        ),
        migrations.AddField(
            model_name='ora_tab_privs',
            name='table',
            field=models.ForeignKey(to='sql.ora_tables'),
        ),
        migrations.AlterUniqueTogether(
            name='operation_ctl',
            unique_together=set([('data_type', 'opt_type')]),
        ),
        migrations.AlterUniqueTogether(
            name='ora_tab_privs',
            unique_together=set([('username', 'table')]),
        ),
    ]
