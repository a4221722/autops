# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbmonitor', '0003_auto_20180529_1553'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='ora_awr_report',
            unique_together=set([('cluster_name', 'end_snap_id')]),
        ),
    ]
