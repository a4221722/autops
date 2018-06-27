# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MyComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('object_pk', models.TextField(verbose_name='object ID')),
                ('user_name', models.CharField(verbose_name="user's name", max_length=50, blank=True)),
                ('user_email', models.EmailField(verbose_name="user's email address", max_length=254, blank=True)),
                ('user_url', models.URLField(verbose_name="user's URL", blank=True)),
                ('comment', models.TextField(verbose_name='comment', max_length=3000)),
                ('submit_date', models.DateTimeField(verbose_name='date/time submitted', db_index=True, default=None)),
                ('ip_address', models.GenericIPAddressField(verbose_name='IP address', blank=True, null=True, unpack_ipv4=True)),
                ('is_public', models.BooleanField(verbose_name='is public', default=True, help_text='Uncheck this box to make the comment effectively disappear from the site.')),
                ('is_removed', models.BooleanField(verbose_name='is removed', default=False, help_text='Check this box if the comment is inappropriate. A "This comment has been removed" message will be displayed instead.')),
                ('content_type', models.ForeignKey(verbose_name='content type', related_name='content_type_set_for_mycomment', to='contenttypes.ContentType')),
                ('site', models.ForeignKey(to='sites.Site')),
                ('user', models.ForeignKey(verbose_name='user', blank=True, null=True, related_name='mycomment_comments', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-submit_date'],
            },
        ),
    ]
