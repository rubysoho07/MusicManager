from django.conf.urls import url
from django.contrib.auth import views as auth_views
from mm_user.views import *

# Register application namespace
app_name = 'user'

# URL patterns for users.
urlpatterns = [
    # Login and logout.
    url(r'^login/$', auth_views.LoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),

    # Create an user.
    url(r'^create/', UserCreateView.as_view(), name='create'),
    url(r'^create_done/', UserCreateDoneTV.as_view(), name='create_done'),

    # Show profile of an user.
    url(r'^profile/(?P<pk>\d+)$', UserDetailView.as_view(), name='user_profile'),

    # Show profile of logged user.
    url(r'^main/$', UserMainView.as_view(), name='main'),

    # Modify user's information.
    url(r'^update/$', UserUpdateView.as_view(), name='update'),

    # Delete an user.
    url(r'^delete/$', UserDeleteView.as_view(), name='delete'),

    # Change password for an user.
    url(r'^change_pw/$', auth_views.PasswordChangeView.as_view(), {'post_change_redirect': 'user:password_change_done'},
        name='password_change'),
    url(r'^change_pw/done/$', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    # Reset password for an user.
    url(r'^pw_reset/$', auth_views.PasswordResetView.as_view(), {'post_reset_redirect': 'user:password_reset_done'},
        name='password_reset'),
    url(r'^pw_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(), {'post_reset_redirect': 'user:password_reset_complete'},
        name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Add an album to an user's album list.
    url(r'^user_album_add/$', UserAlbumAddView.as_view(), name='user_album_add'),
    url(r'^user_album_add/(?P<pk>\d+)$', UserAlbumAddConfirmView.as_view(), name='user_album_add_confirm'),

    # Delete an album from an user's album list.
    url(r'^user_album_delete/(?P<pk>\d+)$', UserAlbumDeleteView.as_view(), name='user_album_delete'),

    # Set score for an album.
    url(r'^rating/(?P<pk>\d+)$', UserAlbumRatingView.as_view(), name='user_album_rating'),

    # Process abnormal request.
    url(r'^rating/$', UserAbnormalRequestRV.as_view(), name='user_album_rating_no_argument'),

    # Get intersection of album lists between 2 users.
    url(r'^intersection/(?P<pk>\d+)$', UserIntersectionView.as_view(), name='intersection'),

    # Search an album from an user's album list.
    url(r'^user_album_search/$', UserAlbumSearchFV.as_view(), name='user_album_search'),
]
