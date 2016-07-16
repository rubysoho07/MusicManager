from django.contrib import admin

from .models import Album, AlbumTrack

# Register your models here.
admin.site.register(Album)
admin.site.register(AlbumTrack)