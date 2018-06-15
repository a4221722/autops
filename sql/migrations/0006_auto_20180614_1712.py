# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sql', '0005_ora_tables_instance_id'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='ora_tables',
            unique_together=set([('instance_id', 'schema_name', 'table')]),
        ),
        migrations.RemoveField(
            model_name='ora_tables',
            name='cluster_name',
        ),
    ]
