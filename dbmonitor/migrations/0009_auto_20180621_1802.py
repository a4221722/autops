# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbmonitor', '0008_os_host_config'),
    ]

    operations = [
        migrations.AlterField(
            model_name='os_host_config',
            name='host_ip',
            field=models.CharField(verbose_name='主机地址', max_length=200, unique=True),
        ),
    ]
