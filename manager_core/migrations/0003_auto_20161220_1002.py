# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-20 01:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager_core', '0002_auto_20160716_2159'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='foreign_artist',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='album_cover_file',
            field=models.ImageField(max_length=200, upload_to='manager_core/cover_files'),
        ),
    ]