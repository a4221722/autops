# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbmonitor', '0004_auto_20180529_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='ora_awr_report',
            name='status',
            field=models.CharField(verbose_name='状态', max_length=200, default=None),
            preserve_default=False,
        ),
    ]
