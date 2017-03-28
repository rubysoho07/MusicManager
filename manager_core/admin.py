from django.contrib import admin

from .models import Album, AlbumTrack, AlbumComment


class AlbumTrackInline(admin.TabularInline):
    """Admin page to add track for an album"""
    model = AlbumTrack
    extra = 1


class AlbumAdmin(admin.ModelAdmin):
    """Admin for the information of an album"""
    inlines = [AlbumTrackInline]
    list_display = ("album_artist", "album_title")


class AlbumTrackAdmin(admin.ModelAdmin):
    """Admin for the information of a track"""
    list_display = ("album", "disk", "track_num", "track_title", "track_artist")


class AlbumCommentAdmin(admin.ModelAdmin):
    """Admin for an comment for an album."""
    list_display = ("user", "album", "comment", "add_date")

# Register your models here.
admin.site.register(Album, AlbumAdmin)
admin.site.register(AlbumTrack, AlbumTrackAdmin)
admin.site.register(AlbumComment, AlbumCommentAdmin)
