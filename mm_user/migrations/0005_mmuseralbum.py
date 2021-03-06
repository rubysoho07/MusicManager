# Generated by Django 1.10.5 on 2017-02-21 07:22
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('manager_core', '0001_initial'),
        ('mm_user', '0004_remove_mmuser_albums'),
    ]

    operations = [
        migrations.CreateModel(
            name='MmUserAlbum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_time', models.DateTimeField(auto_now_add=True)),
                ('score', models.FloatField(null=True)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager_core.Album')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
