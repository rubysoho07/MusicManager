import json

from django.shortcuts import render, redirect, get_object_or_404

from django.db.models import Q

from django.views.generic.base import TemplateView, View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, FormView

from django.urls import reverse_lazy

from .forms import AlbumSearchForm, AlbumParseRequestForm
from .models import Album, AlbumTrack, AlbumComment
from .music_parser import MusicParser

# To save album cover image.
import requests
from io import BytesIO


# Create your views here.
def make_base_album_info(album, cover_url):
    """
    Make single view for album information.
    """
    album_info = dict()

    album_info['album'] = album
    album_info['cover_url'] = cover_url

    return album_info


def make_album_info(album, cover_url):
    """
    If user want to get album information from database,
    attach additional information for an album.
    """
    album_info = make_base_album_info(album, cover_url)

    album_info['show_owner_count'] = True
    album_info['show_average_rating'] = True

    return album_info


def make_link_enable(album_info):
    """
    If the link for an album needs to be enabled, make link enabled.
    """
    album_info['link'] = True
    return album_info


def make_user_add_album(album_info):
    """
    Make link of adding album to the list for an user.
    """
    album_info['add_user_list'] = True
    return album_info


def make_user_delete_album(album_info, user_album_id):
    """
    Make link of deleting album from the list for an user.
    """
    album_info['delete_user_list'] = True
    album_info['user_album_id'] = user_album_id
    return album_info


def make_user_add_delete_album(album_info, album, user):
    """
    Check whether making add to list or delete from list button.
    """
    if user.is_authenticated():
        my_album = album.mmuseralbum_set.filter(Q(user=user))
        if len(my_album) == 0:
            album_info = make_user_add_album(album_info)
        else:
            album_info = make_user_delete_album(album_info, my_album[0].id)

    return album_info


def make_album_list(object_list, user):
    """
    Make album list for album list views.
    """
    album_list = list()

    for item in object_list:
        # Make album information.
        item_dict = make_album_info(item, item.album_cover_file.url)
        item_dict = make_link_enable(item_dict)
        item_dict = make_user_add_delete_album(item_dict, item, user)

        album_list.append(item_dict)

    return album_list


class AlbumLV(ListView):
    """
    List of all albums.
    """
    model = Album
    paginate_by = 10
    queryset = Album.objects.all().order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(AlbumLV, self).get_context_data(**kwargs)

        # Get count for all albums.
        context['albums_number'] = self.get_queryset().count()

        # Manipulate object list.
        context['object_list'] = make_album_list(self.object_list, self.request.user)

        return context


class SearchFV(FormView):
    """
    Search albums from database. (by Artist/Album title)
    """
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
        context['object_list'] = make_album_list(result, self.request.user)

        return render(self.request, self.template_name, context)


class AlbumParseView(FormView):
    """
    Parse album information to add album.
    """
    form_class = AlbumParseRequestForm
    template_name = 'manager_core/album_parse.html'

    def form_valid(self, form):
        # Context dictionary.
        context = dict()

        # Original URL from submitted value.
        original_url = self.request.POST['album_url']

        # Parse URL and make JSON values.
        new_url = MusicParser.check_input(original_url)

        if new_url is None:
            # Error on parsing URL.
            context['form'] = form
            context['success'] = False
            context['error'] = True
            return render(self.request, self.template_name, context=context)
        else:
            parsed_data = MusicParser.get_parsed_data(new_url)

        # JSON data -> Data for user.
        json_data = json.loads(parsed_data)

        # Album title, cover, artist: unicode data.
        context['parsed_album'] = make_base_album_info(Album(album_title=json_data['album_title'],
                                                             album_artist=json_data['artist']),
                                                       json_data['album_cover'])

        # Album track: a list.
        # (A track of track list is to an dict, because a track is JSON object.)
        tracks = json_data['tracks']

        # Dividing all tracks per disk.
        disk_num = 1
        disks = []

        track_list = list(track for track in tracks if track['disk'] == disk_num)

        while len(track_list) != 0:
            disks.append(track_list)
            disk_num += 1
            track_list = list(track for track in tracks if track['disk'] == disk_num)

        context['disks'] = disks
        context['parsed_data'] = parsed_data
        context['original_url'] = original_url
        context['form'] = form
        context['success'] = True
        return render(self.request, self.template_name, context=context)


class AlbumCreateView(View):
    """
    Add album to database.
    """

    def post(self, request, *args, **kwargs):
        # Get JSON data
        parsed_data = request.POST['album_data']

        # Get album number to make file name of image file for an album cover.
        if Album.objects.count() == 0:
            album_num = 1
        else:
            album_num = Album.objects.all().order_by("-id")[0].id + 1

        # Add JSON data to database
        json_data = json.loads(parsed_data)

        album = Album(album_artist=json_data['artist'],
                      album_title=json_data['album_title'],
                      album_url=request.POST['album_url'])

        # Save album cover image.
        if MusicParser.check_album_cover_pattern(json_data['album_cover']):
            album.album_cover_file.save(
                                "album_" + format(album_num, '08') + ".jpg",
                                BytesIO(requests.get(json_data['album_cover']).content)
                            )
        else:
            album.album_cover_file.name = "manager_core/cover_files/no_cover.jpg"

        album.save()

        # Add track data to database
        new_album_track = json_data['tracks']

        for track in new_album_track:
            new_track = AlbumTrack(album=album, disk=track['disk'],
                                   track_num=track['track_num'], track_title=track['track_title'],
                                   track_artist=track['track_artist'])
            new_track.save()

        # If user is authenticated, redirect to add album in user's list.
        if request.user.is_authenticated():
            return redirect("user:user_album_add_confirm", pk=album.id)
        else:
            return redirect("index")


class AlbumDV(DetailView):
    """
    Detailed album information.
    """
    model = Album

    def get_context_data(self, **kwargs):
        context = super(AlbumDV, self).get_context_data(**kwargs)

        # Get album information.
        context_album = make_album_info(self.object, self.object.album_cover_file.url)
        context_album = make_user_add_delete_album(context_album, self.object, self.request.user)

        context['album'] = context_album
        # Get track list (per disk).
        disk_num = 1
        disks = []

        track_list = self.object.albumtrack_set.filter(disk=disk_num).order_by('track_num')

        while len(track_list) != 0:
            disks.append(track_list)
            disk_num += 1
            track_list = self.object.albumtrack_set.filter(disk=disk_num).order_by('track_num')

        context['disks'] = disks

        # Get comment list.
        comments = self.object.albumcomment_set.all().order_by('-add_date')
        context['comments'] = comments

        # Get users list.
        users = self.object.mmuseralbum_set.all()
        context['users'] = users
        return context


class AlbumDeleteView(DeleteView):
    """
    Delete album information from database.
    """
    model = Album

    # If delete completed, redirect to album list.
    success_url = reverse_lazy('index')

    def delete(self, request, *args, **kwargs):
        # remove cover file from media directory.
        self.get_object().album_cover_file.delete()

        # remove instance of Album.
        return super(AlbumDeleteView, self).delete(request, *args, **kwargs)


class Error404View(TemplateView):
    """
    View for 404 error
    """
    template_name = "manager_core/404.html"


class Error500View(TemplateView):
    """
    View for 500 error
    """
    template_name = "manager_core/500.html"


class AlbumCommentAddView(View):
    """
    Add comments
    """
    def post(self, request, *args, **kwargs):
        # Get user, album, comment
        user = request.user
        album = get_object_or_404(Album, pk=request.POST['album_id'])
        comment = request.POST['comment']

        # Make new object and save it to the database.
        album_comment = AlbumComment(user=user, album=album, comment=comment)
        album_comment.save()

        # Redirect to detailed page of the album.
        return redirect('manager_core:album', pk=album.id)


class AlbumCommentDeleteView(DeleteView):
    """
    Delete comments
    """
    model = AlbumComment

    # Save success_url to redirect to album detail page.
    def get_success_url(self):
        return reverse_lazy('manager_core:album', kwargs={'pk': self.get_object().album.id})

    # To delete without confirmation.
    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super(AlbumCommentDeleteView, self).delete(request, *args, **kwargs)
