# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-22 03:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager_core', '0006_auto_20170322_1218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='album_cover_file',
            field=models.ImageField(blank=True, default='manager_core/cover_files/no_cover.jpg', max_length=200, null=True, upload_to='manager_core/cover_files'),
        ),
    ]
