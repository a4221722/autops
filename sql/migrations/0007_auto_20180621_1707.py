# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sql', '0006_auto_20180614_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ora_primary_config',
            name='cluster_name',
            field=models.CharField(verbose_name='实例名称', max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='workflow',
            name='cluster_name',
            field=models.CharField(verbose_name='集群名称', max_length=500),
        ),
    ]
