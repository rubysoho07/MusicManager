# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-06 09:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mm_user', '0007_auto_20170227_0816'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mmuseralbum',
            name='score',
            field=models.PositiveSmallIntegerField(default=0, null=True),
        ),
    ]