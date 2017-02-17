# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-17 08:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager_core', '0001_initial'),
        ('mm_user', '0002_auto_20170206_2200'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useralbum',
            name='album',
        ),
        migrations.RemoveField(
            model_name='useralbum',
            name='owner',
        ),
        migrations.AddField(
            model_name='mmuser',
            name='albums',
            field=models.ManyToManyField(to='manager_core.Album'),
        ),
        migrations.DeleteModel(
            name='UserAlbum',
        ),
    ]
