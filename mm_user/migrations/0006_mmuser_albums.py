# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-22 03:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager_core', '0002_album_owner_count'),
        ('mm_user', '0005_mmuseralbum'),
    ]

    operations = [
        migrations.AddField(
            model_name='mmuser',
            name='albums',
            field=models.ManyToManyField(through='mm_user.MmUserAlbum', to='manager_core.Album'),
        ),
    ]
