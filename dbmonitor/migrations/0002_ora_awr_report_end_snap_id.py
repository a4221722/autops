# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbmonitor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ora_awr_report',
            name='end_snap_id',
            field=models.IntegerField(verbose_name='截止快照id', default=0),
            preserve_default=False,
        ),
    ]
