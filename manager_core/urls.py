from django.conf.urls import url

from . import views
from views import AlbumDV, AlbumLV, SearchFV, AlbumDeleteView

# Register application namespace
app_name = 'manager_core'

# URL patterns
urlpatterns = [
    url(r'^$', AlbumLV.as_view(), name='index'),
    url(r'^search/', SearchFV.as_view(), name='search'),
    url(r'^add/', views.add_album, name='add_album'),
    url(r'^add_result/', views.add_result, name='add_result'),
    url(r'^add_action/', views.add_action, name='add_action'),
    url(r'^album/(?P<pk>[0-9]+)/$', AlbumDV.as_view(), name='album'),
    url(r'^delete/(?P<pk>[0-9]+)/$', AlbumDeleteView.as_view(), name='delete'),
]
