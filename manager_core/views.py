from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from .models import Album, AlbumTrack

import music_parser
import re
import json
import os


# Save album cover image and return saved cover image name.
def get_album_cover(original_url):
    # find pattern from these patterns.
    # Naver: http://musicmeta.phinf.naver.net/album/000/645/645112.jpg?type=r204Fll&v=20160623150347
    # Melon: http://cdnimg.melon.co.kr/cm/album/images/006/23/653/623653.jpg
    # Bugs: http://image.bugsm.co.kr/album/images/200/5712/571231.jpg
    # AllMusic: http://cps-static.rovicorp.com/3/JPG_500/MI0002/416/MI0002416076.jpg?partner=allrovi.com
    naver_pattern = re.compile("http://musicmeta[.]phinf[.]naver[.]net/album/.*[.]jpg[?].*")
    melon_pattern = re.compile("http://cdnimg[.]melon[.]co[.]kr/cm/album/images/.*[.]jpg")
    bugs_pattern = re.compile("http://image[.]bugsm[.]co[.]kr/album/images/.*[.]jpg")
    allmusic_pattern = re.compile("http://cps-static[.]rovicorp[.]com/.*[.]jpg.*")

    # Check Naver pattern.
    result = naver_pattern.search(original_url)

    if result:
        music_parser.save_image(original_url,
                                "manager_core/static/manager_core/images/naver_"
                                + original_url.split("/")[-1].split("?")[0])
        return "naver_" + original_url.split("/")[-1].split("?")[0]

    # Check Melon pattern.
    result = melon_pattern.search(original_url)

    if result:
        music_parser.save_image(original_url,
                                "manager_core/static/manager_core/images/melon_" + original_url.split("/")[-7])
        return "melon_" + original_url.split("/")[-7]

    # Check Bugs pattern.
    result = bugs_pattern.search(original_url)

    if result:
        music_parser.save_image(original_url,
                                "manager_core/static/manager_core/images/bugs_" + original_url.split("/")[-1])
        return "bugs_" + original_url.split("/")[-1]

    # Check AllMusic pattern.
    result = allmusic_pattern.search(original_url)

    if result:
        music_parser.save_image(original_url,
                                "manager_core/static/manager_core/images/allmusic_"
                                + original_url.split("/")[-1].split("?")[0])
        return "allmusic_" + original_url.split("/")[-1].split("?")[0]

    return None


# Create your views here.


# First page. (List of albums I've bought.)
def index(request):
    # Get all albums (to List).
    all_album_list = Album.objects.all().order_by('-id')

    albums_number = len(all_album_list)

    # Get data of current page. (Default is first page.)
    current_page = int(request.GET.get('page', '1'))

    if current_page != 1:
        start_num = (current_page - 1) * 10
    else:
        start_num = 0

    if albums_number - start_num < 10:
        end_num = albums_number
    else:
        end_num = start_num + 10

    album_list = all_album_list[start_num:end_num]

    # Get number of total pages.
    if albums_number % 10 == 0:
        total_pages = (albums_number / 10)
    else:
        total_pages = (albums_number / 10) + 1

    return render(request, 'manager_core/index.html',
                  {'album_list': album_list,
                   'current_page': current_page,
                   'start_num': start_num,
                   'pages_list': range(1, total_pages + 1),
                   'albums_number': albums_number})


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


# Add album information to database.
def add_action(request):
    # Get JSON data
    parsed_data = request.POST['album_data']

    # Add JSON data to database
    json_data = json.loads(parsed_data)

    new_album_title = json_data['album_title']
    new_album_cover = get_album_cover(json_data['album_cover'])
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

    # Dividing all tracks per disk.
    disk_num = 1
    disks = []

    track_list = album.albumtrack_set.filter(disk=disk_num)

    while len(track_list) != 0:
        disks.append(track_list)
        disk_num += 1
        track_list = album.albumtrack_set.filter(disk=disk_num)

    return render(request, 'manager_core/album_detail.html', {'album': album, 'disks': disks})


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
    os.remove("manager_core/static/manager_core/images/" + album_cover_file)

    return render(request, 'manager_core/delete_album_complete.html',
                  {
                      'album_artist': album_artist,
                      'album_title': album_title
                  })


# View for 404 error
def custom_page_not_found(request):
    return render(request, 'manager_core/404.html')


# View for 500 error
def custom_internal_server_error(request):
    return render(request, 'manager_core/500.html')
