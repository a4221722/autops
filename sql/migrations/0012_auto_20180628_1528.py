# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sql', '0011_auto_20180628_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflow',
            name='affirm_time',
            field=models.DateTimeField(verbose_name='结束时间', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='workflow',
            name='status',
            field=models.CharField(max_length=50, choices=[('自动审核中', '自动审核中'), ('等待审核人审核', '等待审核人审核'), ('自动审核不通过', '自动审核不通过'), ('执行中', '执行中'), ('等待手工执行', '等待手工执行'), ('人工终止流程', '人工终止流程'), ('自动执行结束', '自动执行结束'), ('执行有异常', '执行有异常'), ('手工执行成功', '手工执行成功'), ('手工执行异常', '手工执行异常')]),
        ),
    ]
