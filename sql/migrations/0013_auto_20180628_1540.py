# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sql', '0012_auto_20180628_1528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workflow',
            name='affirm',
            field=models.CharField(verbose_name='工程师是否确认', max_length=10, default='未确认', choices=[('未确认', '未确认'), ('已确认', '已确认')]),
        ),
    ]
