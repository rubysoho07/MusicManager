from django.contrib import admin

from .models import Album, AlbumTrack


# Track Inline.
class AlbumTrackInline(admin.TabularInline):
    model = AlbumTrack
    extra = 1


# Album Admin
class AlbumAdmin(admin.ModelAdmin):
    inlines = [AlbumTrackInline]
    list_display = ("album_artist", "album_title")


# Album Track Admin
class AlbumTrackAdmin(admin.ModelAdmin):
    list_display = ("album", "disk", "track_num", "track_title", "track_artist")

# Register your models here.
admin.site.register(Album, AlbumAdmin)
admin.site.register(AlbumTrack, AlbumTrackAdmin)
