# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sql', '0002_auto_20180525_1051'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflow',
            name='data_change_type',
            field=models.CharField(verbose_name='数据变更类型', max_length=50, default='数据修订', choices=[('数据修订', '数据修订'), ('数据初始化', '数据初始化'), ('数据迁移', '数据迁移')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='workflow',
            name='reason',
            field=models.CharField(verbose_name='原因', max_length=200, default='测试'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='workflow',
            name='message',
            field=models.TextField(verbose_name='备注说明', null=True),
        ),
    ]
