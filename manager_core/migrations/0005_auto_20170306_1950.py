# Generated by Django 1.10.5 on 2017-03-06 10:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager_core', '0004_album_album_rating'),
    ]

    operations = [
        migrations.RenameField(
            model_name='album',
            old_name='album_rating',
            new_name='average_rating',
        ),
    ]
