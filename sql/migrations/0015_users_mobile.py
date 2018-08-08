# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sql', '0014_auto_20180703_1136'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='mobile',
            field=models.CharField(verbose_name='手机号', max_length=20, null=True),
        ),
    ]
