# Generated by Django 1.10.5 on 2017-02-26 23:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mm_user', '0006_mmuser_albums'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mmuseralbum',
            options={'ordering': ['-add_time']},
        ),
    ]
