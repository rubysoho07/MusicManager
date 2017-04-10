import json
import re

from django.shortcuts import render, redirect, get_object_or_404

from django.db.models import Q

from django.views.generic.base import View
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
def make_base_album_info(album, cover_file):
    """Make single view for album information."""

    album_info = dict()

    album_info['album'] = album

    # Check file is Null
    if bool(cover_file) is False:
        album_info['cover_file'] = None
    else:
        if hasattr(cover_file, 'url'):
            album_info['cover_file'] = cover_file.url
        else:
            # Use external cover file.
            album_info['cover_file'] = cover_file

    return album_info


def make_album_info(album, cover_url):
    """Make single view for an album, link for an artist, count of owners, and average ratings."""
    album_info = make_base_album_info(album, cover_url)

    album_info['artist_link'] = True
    album_info['show_owner_count'] = True
    album_info['show_average_rating'] = True

    return album_info


def make_link_enable(album_info):
    """Make link to detail page for an album enabled."""
    album_info['link'] = True
    return album_info


def make_user_add_album(album_info):
    """Make link of adding album to the list for an user."""

    album_info['add_user_list'] = True
    return album_info


def make_user_delete_album(album_info, user_album_id):
    """Make link to delete album from the list for an user."""

    album_info['delete_user_list'] = True
    album_info['user_album_id'] = user_album_id
    return album_info


def make_user_add_delete_album(album_info, album, user):
    """Make add to list or delete from list button."""

    if user.is_authenticated():
        my_album = album.mmuseralbum_set.filter(Q(user=user))
        if len(my_album) == 0:
            album_info = make_user_add_album(album_info)
        else:
            album_info = make_user_delete_album(album_info, my_album[0].id)

    return album_info


def make_album_list(object_list, user):
    """Make album list for album list views."""

    album_list = list()

    for item in object_list:
        # Make album information.
        item_dict = make_album_info(item, item.album_cover_file)
        item_dict = make_link_enable(item_dict)
        item_dict = make_user_add_delete_album(item_dict, item, user)

        album_list.append(item_dict)

    return album_list


def make_pagination_range(page_num, pages_count):
    """Get page range to omit pages far away from current page."""
    show_first = False
    show_last = False

    # Minimum pages: 5 pages(current page +- 2 pages)
    if pages_count <= 5:
        return show_first, range(1, pages_count+1), show_last

    page_range = [x for x in range(page_num - 2, page_num + 3) if 1 <= x <= pages_count]

    if 1 not in page_range:
        show_first = True

    if pages_count not in page_range:
        show_last = True

    return show_first, page_range, show_last


class AlbumLV(ListView):
    """List of all albums."""

    model = Album
    paginate_by = 10
    queryset = Album.objects.all().order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(AlbumLV, self).get_context_data(**kwargs)

        # Get count for all albums.
        context['albums_number'] = self.get_queryset().count()

        # Manipulate object list.
        paginator, page, page_object_list, _ = self.paginate_queryset(self.get_queryset(), self.paginate_by)
        context['object_list'] = make_album_list(page_object_list, self.request.user)
        context['show_first'], context['page_range'], context['show_last'] = \
            make_pagination_range(page.number, paginator.num_pages)

        return context


class SearchFV(FormView):
    """Search albums from database by title or artist."""

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
    """Parse album information to add album."""

    form_class = AlbumParseRequestForm
    template_name = 'manager_core/album_parse.html'

    @staticmethod
    def make_disks(tracks):
        """Dividing all tracks per disk."""
        disk_num = 1
        disks = []

        track_list = list(track for track in tracks if track['disk'] == disk_num)

        while len(track_list) != 0:
            disks.append(track_list)
            disk_num += 1
            track_list = list(track for track in tracks if track['disk'] == disk_num)

        return disks

    def form_valid(self, form):
        context = dict()
        original_url = self.request.POST['album_url']
        music_parser = MusicParser()

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
        context['parsed_album'] = make_base_album_info(Album(album_title=json_data['album_title'],
                                                             album_artist=json_data['artist']),
                                                       json_data['album_cover'])
        context['disks'] = self.make_disks(json_data['tracks'])
        context['parsed_data'] = parsed_data
        context['original_url'] = original_url
        context['form'] = form
        context['success'] = True
        return render(self.request, self.template_name, context=context)


class AlbumCreateView(View):
    """View to add album to database."""

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
            album.album_cover_file = None

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
    """View to show detailed album information."""

    model = Album

    def get_context_data(self, **kwargs):
        context = super(AlbumDV, self).get_context_data(**kwargs)

        # Get album information.
        context_album = make_album_info(self.object, self.object.album_cover_file)
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


class AlbumCommentAddView(View):
    """Add comments for an album to database."""

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
    """Delete comments for an album from database."""

    model = AlbumComment

    def get_success_url(self):
        """Save success_url to redirect to album detail page."""
        return reverse_lazy('manager_core:album', kwargs={'pk': self.get_object().album.id})

    def get(self, *args, **kwargs):
        """Call post() to delete without confirmation."""
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Delete a comment."""
        return super(AlbumCommentDeleteView, self).delete(request, *args, **kwargs)


class ArtistAlbumListView(AlbumLV):
    """Show list of albums which made by an artist."""
    template_name = 'manager_core/album_artist_list.html'

    def get_artist_name(self):
        """Get artist name from an album and exclude artist name in brackets."""
        pattern = re.compile("(?P<artist>.+)\((?P<foreign_language>.+)\)")
        artist_name = Album.objects.filter(id=self.kwargs['pk'])[0].album_artist

        match = pattern.search(artist_name)

        if match:
            return match.group('artist').strip()
        else:
            return artist_name.strip()

    def get_queryset(self):
        """Get album list which made by an artist."""
        return Album.objects.filter(album_artist__icontains=self.get_artist_name())

    def get_context_data(self, **kwargs):
        """Override get_context_data method and get artist name and count of albums."""
        context = super(ArtistAlbumListView, self).get_context_data(**kwargs)

        context['artist_name'] = self.get_artist_name()
        context['artist_album_count'] = self.get_queryset().count()

        return context
