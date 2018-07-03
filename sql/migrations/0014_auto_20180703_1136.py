# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sql', '0013_auto_20180628_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workflow',
            name='data_change_type',
            field=models.CharField(verbose_name='数据变更类型', max_length=50, choices=[('数据修订', '数据修订'), ('数据初始化', '数据初始化'), ('数据迁移', '数据迁移'), ('表结构变更', '表结构变更')]),
        ),
    ]
