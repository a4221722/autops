# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ora_awr_report',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('cluster_name', models.CharField(verbose_name='实例名称', max_length=50)),
                ('interval', models.CharField(verbose_name='时间区间', max_length=30)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('awr_location', models.FileField(verbose_name='awr报告', upload_to='')),
            ],
            options={
                'verbose_name': 'awr报告',
                'verbose_name_plural': 'awr报告',
            },
        ),
    ]
