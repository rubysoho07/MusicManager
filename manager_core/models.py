from __future__ import unicode_literals

from django.db import models
from django.conf import settings


# Create your models here.
class Album(models.Model):
    """Album consists of artist, title, cover image, URL, and some information."""

    album_artist = models.CharField(max_length=200)
    album_title = models.CharField(max_length=200)
    album_cover_file = models.ImageField(
        upload_to='manager_core/cover_files', max_length=200,
        default='manager_core/cover_files/no_cover.jpg'
    )
    album_url = models.CharField(max_length=200, null=True, default=None, blank=True)
    owner_count = models.IntegerField(default=0, blank=True)
    average_rating = models.FloatField(default=None, null=True, blank=True)

    def __str__(self):
        return self.album_artist + " - " + self.album_title


class AlbumTrack(models.Model):
    """Album track related with an album."""

    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    disk = models.IntegerField()
    track_num = models.IntegerField()
    track_title = models.CharField(max_length=200)
    track_artist = models.CharField(max_length=200)

    def __str__(self):
        return self.track_artist + " - " + self.track_title


class AlbumComment(models.Model):
    """Comment for an album."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500)
    add_date = models.DateTimeField(auto_now_add=True)
