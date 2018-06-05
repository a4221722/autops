# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbmonitor', '0005_ora_awr_report_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ora_awr_report',
            name='status',
            field=models.CharField(verbose_name='状态', max_length=200, default='init'),
        ),
    ]
