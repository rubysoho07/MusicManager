from django.conf.urls import include, url
import django.contrib.auth.views as auth_views
from mm_user.views import UserCreateView, UserCreateDoneTV

# Register application namespace
app_name = 'user'

# URL patterns for authentication
urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': 'users/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^create/', UserCreateView.as_view(), name='create'),
    url(r'^create_done/', UserCreateDoneTV.as_view(), name='create_done'),
]