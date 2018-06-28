# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sql', '0009_auto_20180627_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflow',
            name='operator',
            field=models.CharField(verbose_name='处理人', max_length=50, null=True),
        ),
    ]
