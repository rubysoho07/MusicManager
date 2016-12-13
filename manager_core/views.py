from django.shortcuts import get_object_or_404, render
from django.conf import settings

from .models import Album, AlbumTrack
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

import music_parser
import json
import os


# Create your views here.
# First page. (List of albums I've bought.)
class AlbumLV(ListView):
    model = Album
    paginate_by = 10
    queryset = Album.objects.all().order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(AlbumLV, self).get_context_data(**kwargs)
        context['albums_number'] = len(self.queryset)
        return context


# Search albums from database. (by Artist/Album title)
def search(request):
    return render(request, 'manager_core/search_album.html')


# See search result.
def search_result(request):
    # Get search keywords.
    search_type = request.POST['search_type']
    keyword = request.POST['search_keyword']

    # Search album from database.
    if search_type == "artist":
        result = Album.objects.filter(album_artist__icontains=keyword)
    elif search_type == "album":
        result = Album.objects.filter(album_title__icontains=keyword)
    else:
        return render(request, 'manager_core/search_result.html',
                      {'search_type': search_type,
                       'keyword': keyword,
                       'search_result': []})

    return render(request, 'manager_core/search_result.html',
                  {'search_type': search_type,
                   'keyword': keyword,
                   'search_result': result})


# TODO: Class-based search page.


# Add album from Bugs/Naver music.
def add_album(request):
    return render(request, 'manager_core/add_album.html', {'error': False})


# Add result and confirm add this information or cancel.
def add_result(request):
    # Original URL from submitted value.
    original_url = request.POST['album_url']

    # Parse URL and make JSON values.
    new_url = music_parser.check_input(original_url)

    if new_url == "":
        return render(request, 'manager_core/add_album.html', {'error': True, 'req_url': original_url})
    else:
        parsed_data = music_parser.get_parsed_data(new_url)

    # JSON data -> Data for user.
    json_data = json.loads(parsed_data)

    # Album title, cover, artist: unicode data.
    album_title = json_data['album_title']
    album_cover = json_data['album_cover']
    album_artist = json_data['artist']

    # Album track: a list. 
    # (A track of track list is to an dict, because a track is JSON object.)
    album_track = json_data['tracks']

    # Dividing all tracks per disk.
    disk_num = 1
    disks = []

    track_list = list(track for track in album_track if track['disk'] == disk_num)

    while len(track_list) != 0:
        disks.append(track_list)
        disk_num += 1
        track_list = list(track for track in album_track if track['disk'] == disk_num)

    return render(request, 'manager_core/add_album_confirm.html',
                  {'original_url': original_url,
                   'parsed_data': parsed_data,
                   'album_artist': album_artist,
                   'album_title': album_title,
                   'album_cover': album_cover,
                   'disks': disks})


# TODO: Class-based add album page


# Add album information to database.
def add_action(request):
    # Get JSON data
    parsed_data = request.POST['album_data']

    # Add JSON data to database
    json_data = json.loads(parsed_data)

    new_album_title = json_data['album_title']
    new_album_cover = music_parser.get_album_cover(json_data['album_cover'])
    new_album_artist = json_data['artist']

    album = Album(album_artist=new_album_artist, album_title=new_album_title,
                  album_cover_file=new_album_cover, album_url=request.POST['album_url'])
    album.save()

    # Add track data to database
    new_album_track = json_data['tracks']

    for track in new_album_track:
        new_track = AlbumTrack(album=album, disk=track['disk'],
                               track_num=track['track_num'], track_title=track['track_title'],
                               track_artist=track['track_artist'])
        new_track.save()

    return render(request, 'manager_core/add_album_complete.html',
                  {'album_artist': new_album_artist,
                   'album_title': new_album_title,
                   'album_cover': new_album_cover})


# Detailed album information.
class AlbumDV(DetailView):
    model = Album

    def get_context_data(self, **kwargs):
        context = super(AlbumDV, self).get_context_data(**kwargs)

        disk_num = 1
        disks = []

        track_list = self.object.albumtrack_set.filter(disk=disk_num)

        while len(track_list) != 0:
            disks.append(track_list)
            disk_num += 1
            track_list = self.object.albumtrack_set.filter(disk=disk_num)

        context['disks'] = disks
        return context


# Confirm delete information from database.
def confirm_delete(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    album_title = album.album_title
    album_artist = album.album_artist
    album_cover = album.album_cover_file

    return render(request, 'manager_core/delete_album_confirm.html',
                  {
                      'album_title': album_title,
                      'album_artist': album_artist,
                      'album_cover': album_cover,
                      'album_id': album_id
                  })


# Delete album information from database.
def delete(request):
    album_id = request.POST['album_id']
    album = get_object_or_404(Album, pk=album_id)
    album_artist = album.album_artist
    album_title = album.album_title
    album_cover_file = album.album_cover_file

    album.delete()

    # remove cover file from static directory.
    os.remove(os.path.join(settings.STATIC_ROOT, "manager_core/images/" + album_cover_file))

    return render(request, 'manager_core/delete_album_complete.html',
                  {
                      'album_artist': album_artist,
                      'album_title': album_title
                  })


# TODO: Class based delete page.


# View for 404 error
class Error404View(TemplateView):
    template_name = "manager_core/404.html"


# View for 500 error
class Error500View(TemplateView):
    template_name = "manager_core/500.html"
