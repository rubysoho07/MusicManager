from django.shortcuts import render, redirect
from django.conf import settings

from .models import Album, AlbumTrack
from django.views.generic.base import TemplateView, View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, FormView

from django.urls import reverse_lazy

from forms import AlbumSearchForm, AlbumParseRequestForm

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
        context['albums_number'] = self.get_queryset().count()
        return context


# Search albums from database. (by Artist/Album title)
class SearchFV(FormView):
    form_class = AlbumSearchForm
    template_name = "manager_core/album_search.html"

    def form_valid(self, form):
        search_type = self.request.POST["search_type"]
        keyword = self.request.POST['keyword']
        # Search album from database.
        if search_type == "artist":
            result = Album.objects.filter(album_artist__icontains=keyword)
        elif search_type == "album":
            result = Album.objects.filter(album_title__icontains=keyword)
        else:
            result = []

        context = dict()
        context['form'] = form
        context['search_type'] = search_type
        context['keyword'] = keyword
        context['object_list'] = result

        return render(self.request, self.template_name, context)


# Parse album information to add album.
class AlbumParseView(FormView):
    form_class = AlbumParseRequestForm
    template_name = 'manager_core/album_parse.html'

    def form_valid(self, form):
        # Context dictionary.
        context = dict()

        # Original URL from submitted value.
        original_url = self.request.POST['album_url']

        # Parse URL and make JSON values.
        new_url = music_parser.check_input(original_url)

        if new_url is None:
            # Error on parsing URL.
            context['form'] = form
            context['success'] = False
            context['error'] = True
            return render(self.request, self.template_name, context=context)
        else:
            parsed_data = music_parser.get_parsed_data(new_url)

        # JSON data -> Data for user.
        json_data = json.loads(parsed_data)

        # Album title, cover, artist: unicode data.
        context['album_title'] = json_data['album_title']
        context['album_cover'] = json_data['album_cover']
        context['album_artist'] = json_data['artist']

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

        context['disks'] = disks
        context['parsed_data'] = parsed_data
        context['original_url'] = original_url
        context['form'] = form
        context['success'] = True
        return render(self.request, self.template_name, context=context)


# Add album to database.
class AlbumCreateView(View):

    def post(self, request, *args, **kwargs):
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

        return redirect("manager_core:index")


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


# Delete album information from database.
class AlbumDeleteView(DeleteView):
    model = Album

    # If delete completed, redirect to album list.
    success_url = reverse_lazy('manager_core:index')

    def delete(self, request, *args, **kwargs):
        # remove cover file from static directory.
        if settings.DEBUG:
            os.remove(os.path.join(settings.STATICFILES_DIRS[0], "manager_core/images/"
                                   + self.get_object().album_cover_file))
        else:
            os.remove(os.path.join(settings.STATIC_ROOT, "manager_core/images/"
                                   + self.get_object().album_cover_file))
        return super(AlbumDeleteView, self).delete(request, *args, **kwargs)


# View for 404 error
class Error404View(TemplateView):
    template_name = "manager_core/404.html"


# View for 500 error
class Error500View(TemplateView):
    template_name = "manager_core/500.html"
