from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from .models import Album, AlbumTrack

import music_parser
import re
import json

# Create your views here.

# First page. (List of albums I've bought.)
def index(request):
    # Get all albums (to List).
    album_list = Album.objects.all()
    return render(request, 'manager_core/index.html', {'album_list': album_list})

# Search albums from database. (by Artist/Album title)
def search(request):
    return HttpResponse("Search album by Artist/Album title.")

# See search result.
def search_result(request):
    return HttpResponse("Search result.")

# Add album from Bugs/Naver music.
def add_album(request):
    return render(request, 'manager_core/add_album.html')

# Add result and confirm add this information or cancel.
def add_result(request):

    # Original URL from submitted value.
    original_url = request.POST['album_url']

    # Parse URL and make JSON values.
    new_url = music_parser.check_input (original_url)

    if new_url == "":
        parsed_data = ""
    else:
        bugs_pattern = re.compile("bugs[.]co[.]kr")
        naver_music_pattern = re.compile("music[.]naver[.]com")

        # if Bugs URL, run get_bugs_data()
        m = bugs_pattern.search(new_url)

        if m:
            parsed_data = music_parser.get_bugs_data(new_url)
        
        # if Naver Music URL, run get_naver_music_data()
        m = naver_music_pattern.search(new_url)

        if m:
            parsed_data = music_parser.get_naver_music_data(new_url)
    
    # JSON data -> HTML data (for user)
    json_data = json.loads(parsed_data)

    album_title = json_data['album_title']
    album_cover = json_data['album_cover']
    album_artist = json_data['artist']
    album_track = json_data['tracks']

    return render(request, 'manager_core/add_album_confirm.html', 
                    {'original_url': original_url, 
                     'parsed_data': parsed_data,
                     'album_artist': album_artist,
                     'album_title': album_title,
                     'album_cover': album_cover,
                     'tracks': album_track})

# Add album information to database.
def add_action(request):
    
    # Get JSON data
    parsed_data = request.POST['album_data']
    
    # Add JSON data to database
    json_data = json.loads(parsed_data)

    new_album_title = json_data['album_title']
    new_album_cover = json_data['album_cover']
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

# See album detail information
def see_album(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    track_list = album.albumtrack_set.all()

    return render(request, 'manager_core/album_detail.html', {'album': album, 'tracks': track_list})

# Confirm delete information from database.
def confirm_delete(request):
    return HttpResponse("Confirm to delete album from database")

# Delete album information from database.
def delete(request):
    return HttpResponse("Delete album")