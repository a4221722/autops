# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbmonitor', '0007_auto_20180605_1307'),
    ]

    operations = [
        migrations.CreateModel(
            name='os_host_config',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('host_name', models.CharField(verbose_name='主机名称', max_length=50, unique=True)),
                ('host_ip', models.CharField(verbose_name='主机地址', max_length=200)),
                ('host_port', models.IntegerField(verbose_name='主机ssh端口', default=22)),
                ('host_user', models.CharField(verbose_name='主机用户名', max_length=100)),
                ('host_password', models.CharField(verbose_name='主机密码', max_length=100)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
                ('snap_flag', models.IntegerField(verbose_name='快照标志位', default=0)),
            ],
            options={
                'verbose_name': '主机信息',
                'verbose_name_plural': '主机信息',
            },
        ),
    ]
