# Generated by Django 1.10.5 on 2017-02-21 07:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mm_user', '0003_auto_20170217_1720'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mmuser',
            name='albums',
        ),
    ]
