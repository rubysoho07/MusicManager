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
]
