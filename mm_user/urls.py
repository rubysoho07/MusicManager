from django.conf.urls import url
import django.contrib.auth.views as auth_views
from mm_user.views import *

# Register application namespace
app_name = 'user'

# URL patterns for authentication
urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': 'users/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^create/', UserCreateView.as_view(), name='create'),
    url(r'^create_done/', UserCreateDoneTV.as_view(), name='create_done'),
    url(r'^profile/(?P<pk>\d+)$', UserDetailView.as_view(), name='user_profile'),
    url(r'^main/$', UserMainView.as_view(), name='main'),
    url(r'^update/$', UserUpdateView.as_view(), name='update'),
    url(r'^delete/$', UserDeleteView.as_view(), name='delete'),
    url(r'^change_pw/$', auth_views.password_change, {'post_change_redirect': 'user:password_change_done',
                                                      'template_name': 'users/password_change.html'},
        name='password_change'),
    url(r'^change_pw/done/$', auth_views.password_change_done, {'template_name': 'users/password_change_done.html'},
        name='password_change_done'),
    url(r'^user_album_add/$', UserAlbumAddView.as_view(), name='user_album_add'),
    url(r'^user_album_add/(?P<pk>\d+)$', UserAlbumAddConfirmView.as_view(), name='user_album_add_confirm'),
    url(r'^user_album_delete/(?P<pk>\d+)$', UserAlbumDeleteView.as_view(), name='user_album_delete'),
    url(r'^rating/(?P<pk>\d+)$', UserAlbumRatingView.as_view(), name='user_album_rating'),
    url(r'^rating/$', UserAbnormalRequestRV.as_view(), name='user_album_rating_no_argument'),

    url(r'^intersection/(?P<pk>\d+)$', UserIntersectionView.as_view(), name='intersection'),
]
