import json
import re
import traceback

from django.core.mail import EmailMessage

from django.conf import settings

from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template

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
class AlbumLV(ListView):
    """List of all albums."""

    model = Album
    paginate_by = 10
    queryset = Album.objects.all().order_by('-id')


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
        context['object_list'] = result

        return render(self.request, self.template_name, context)


class AlbumParseView(FormView):
    """Parse album information to add album."""

    form_class = AlbumParseRequestForm
    template_name = 'manager_core/album_parse.html'

    ERR_INVALID_URL = "유효하지 않은 URL 입니다. 다시 입력해 주세요."
    ERR_ON_PARSING = "앨범 정보를 가져오는 중 오류가 발생했습니다."

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

        try:
            new_url, parser = MusicParser.check_input(original_url)

            if new_url is None:
                # Error on parsing URL.
                context['form'] = form
                context['success'] = False
                context['error'] = self.ERR_INVALID_URL
                return render(self.request, self.template_name, context=context)
            else:
                parsed_data = parser.get_parsed_data(new_url)

            # JSON data -> Data for user.
            json_data = json.loads(parsed_data)

            # Album title, cover, artist: unicode data.
            context['album'] = Album(album_title=json_data['album_title'], album_artist=json_data['artist'])
            context['external_cover'] = json_data['album_cover']
            context['disks'] = self.make_disks(json_data['tracks'])
            context['parsed_data'] = parsed_data
            context['original_url'] = original_url
            context['form'] = form
            context['success'] = True
        except Exception as e:
            context['form'] = form
            context['success'] = False
            context['error'] = self.ERR_ON_PARSING

            # Send email to report error.
            if settings.DEBUG is False:
                email_context = {
                    'site': original_url,
                    'exception': e,
                    'traceback': traceback.format_exc()
                }
                message = get_template('manager_core/error_report_parsing.html').render(email_context)
                error_email = EmailMessage('[MusicManager] Parsing Error Report',
                                           message,
                                           settings.SERVER_EMAIL,
                                           settings.ADMINS)
                error_email.content_subtype = 'html'
                error_email.send(fail_silently=True)

            return render(self.request, self.template_name, context=context)

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
        return Album.objects.filter(album_artist__icontains=self.get_artist_name()).order_by('-id')

    def get_context_data(self, **kwargs):
        """Override get_context_data method and get artist name and count of albums."""
        context = super(ArtistAlbumListView, self).get_context_data(**kwargs)

        context['artist_name'] = self.get_artist_name()
        context['artist_album_count'] = self.get_queryset().count()

        return context
