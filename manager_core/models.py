from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Album(models.Model):
    album_artist = models.CharField(max_length=200)
    album_title = models.CharField(max_length=200)
    album_cover_file = models.CharField(max_length=200)
    album_url = models.CharField(max_length=200)

class AlbumTrack(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    disk = models.IntegerField()
    track_num = models.IntegerField()
    track_title = models.CharField(max_length=200)
    track_artist = models.CharField(max_length=200)
