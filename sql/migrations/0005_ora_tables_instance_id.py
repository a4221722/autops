# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sql', '0004_auto_20180525_1149'),
    ]

    operations = [
        migrations.AddField(
            model_name='ora_tables',
            name='instance_id',
            field=models.IntegerField(verbose_name='实例id', default=1),
            preserve_default=False,
        ),
    ]
