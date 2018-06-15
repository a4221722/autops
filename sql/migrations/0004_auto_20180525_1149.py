# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sql', '0003_auto_20180525_1132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workflow',
            name='status',
            field=models.CharField(max_length=50, choices=[('已正常结束', '已正常结束'), ('人工终止流程', '人工终止流程'), ('自动审核中', '自动审核中'), ('等待审核人审核', '等待审核人审核'), ('执行中', '执行中'), ('自动审核不通过', '自动审核不通过'), ('执行有异常', '执行有异常'), ('等待手工执行', '等待手工执行'), ('手工执行成功', '手工执行成功'), ('手工执行异常', '手工执行异常')]),
        ),
    ]
