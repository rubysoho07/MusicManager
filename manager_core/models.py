from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

from django.db import models


# Create your models here.
@python_2_unicode_compatible
class Album(models.Model):
    album_artist = models.CharField(max_length=200)
    album_title = models.CharField(max_length=200)
    album_cover_file = models.ImageField(upload_to='manager_core/cover_files', max_length=200)
    album_url = models.CharField(max_length=200, null=True)

    # Override __unicode__ method to display album artist and title.
    def __str__(self):
        return self.album_artist + " - " + self.album_title


@python_2_unicode_compatible
class AlbumTrack(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    disk = models.IntegerField()
    track_num = models.IntegerField()
    track_title = models.CharField(max_length=200)
    track_artist = models.CharField(max_length=200)

    # Override __unicode__ method to display song artist and title.
    def __str__(self):
        return self.track_artist + " - " + self.track_title
