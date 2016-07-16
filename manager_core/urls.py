from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search/', views.search, name='search'),
    url(r'^search_result/', views.search_result, name='search_result'),
    url(r'^add/', views.add_album, name='add_album'),
    url(r'^add_result/', views.add_result, name='add_result'),
    url(r'^add_action/', views.add_action, name='add_action'),
    url(r'^album/', views.see_album, name='album'),
    url(r'^confirm_delete/', views.confirm_delete, name='confirm_delete'),
    url(r'^delete/', views.delete, name='delete'),
]