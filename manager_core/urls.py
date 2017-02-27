from django.conf.urls import url

from views import AlbumDV, AlbumLV, SearchFV, AlbumDeleteView, AlbumParseView, AlbumCreateView
from views import AlbumCommentAddView, AlbumCommentDeleteView

# Register application namespace
app_name = 'manager_core'

# URL patterns
urlpatterns = [
    url(r'^$', AlbumLV.as_view(), name='index'),
    url(r'^search/', SearchFV.as_view(), name='search'),
    url(r'^add/', AlbumParseView.as_view(), name='add_album'),
    url(r'^add_action/', AlbumCreateView.as_view(), name='add_action'),
    url(r'^album/(?P<pk>[0-9]+)/$', AlbumDV.as_view(), name='album'),
    url(r'^delete/(?P<pk>[0-9]+)/$', AlbumDeleteView.as_view(), name='delete'),
    url(r'^add_comment/', AlbumCommentAddView.as_view(), name='add_comment'),
    url(r'^delete_comment/(?P<pk>[0-9]+)/$', AlbumCommentDeleteView.as_view(), name='delete_comment'),
]
