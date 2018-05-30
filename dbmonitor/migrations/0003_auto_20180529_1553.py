# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbmonitor', '0002_ora_awr_report_end_snap_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ora_awr_report',
            name='awr_location',
            field=models.CharField(verbose_name='awr报告', max_length=200),
        ),
    ]
