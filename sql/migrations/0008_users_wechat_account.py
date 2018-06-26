# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sql', '0007_auto_20180621_1707'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='wechat_account',
            field=models.CharField(verbose_name='企业微信名', max_length=50, null=True),
        ),
    ]
