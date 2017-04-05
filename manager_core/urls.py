from django.conf.urls import url

from views import AlbumDV, SearchFV, AlbumParseView, AlbumCreateView, ArtistAlbumListView
from views import AlbumCommentAddView, AlbumCommentDeleteView

# Register application namespace
app_name = 'manager_core'

# URL patterns
urlpatterns = [
    # Search album.
    url(r'^search/', SearchFV.as_view(), name='search'),

    # Confirm before adding album to database.
    url(r'^add/', AlbumParseView.as_view(), name='add_album'),

    # Add album to database.
    url(r'^add_action/', AlbumCreateView.as_view(), name='add_action'),

    # Show detailed information for an album.
    url(r'^album/(?P<pk>[0-9]+)/$', AlbumDV.as_view(), name='album'),

    # Add comment for an album to database.
    url(r'^add_comment/', AlbumCommentAddView.as_view(), name='add_comment'),

    # Delete comment for an album from database.
    url(r'^delete_comment/(?P<pk>[0-9]+)/$', AlbumCommentDeleteView.as_view(), name='delete_comment'),

    # Show list of albums for an artist.
    url(r'^artist/(?P<pk>[0-9]+)/$', ArtistAlbumListView.as_view(), name='artist'),
]
