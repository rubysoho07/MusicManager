from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic.base import TemplateView, View, RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView

from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.urlresolvers import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db.models import Q, Avg

from manager_core.models import Album
from manager_core.views import make_album_info, make_link_enable, make_user_add_delete_album, make_album_list
from manager_core.forms import AlbumSearchForm

from mm_user.forms import UserCreationForm, UserChangeForm
from mm_user.models import MmUser, MmUserAlbum


def make_user_album_list(album_score_list, user, authenticated_user):
    """
    Manipulate user's album list.
    """
    user_album_list = list()

    for item in album_score_list:
        album_dict = make_album_info(item.album, item.album.album_cover_file.url)
        album_dict = make_link_enable(album_dict)
        # For current authenticated user.
        album_dict = make_user_add_delete_album(album_dict, item.album, authenticated_user)
        if user == authenticated_user:
            album_dict = make_user_rating_form(album_dict, item.score)

        user_album_list.append(album_dict)

    return user_album_list


def make_user_rating_form(album_info, my_score):
    """
    Make rating form for an item from user's album list.
    """
    album_info['rating_form'] = True
    album_info['my_score'] = my_score
    album_info['score_iterator'] = range(1, 11)
    return album_info


def get_album_intersection_two_users(user1, user2):
    """
    Get album intersection between 2 users.
    """
    user1_album = user1.albums.all()
    user2_album = user2.albums.all()
    return user1_album.filter(id__in=user2_album)


class UserIntersectionView(LoginRequiredMixin, DetailView):
    """
    Get intersection of albums between two users.
    """
    template_name = 'users/user_intersection.html'
    model = MmUser

    def get_context_data(self, **kwargs):
        context = super(UserIntersectionView, self).get_context_data(**kwargs)

        # Get intersection.
        user_album_list = get_album_intersection_two_users(self.object, self.request.user)

        # Pagination for user_album_list (for 10 albums)
        album_list_paginator = Paginator(user_album_list, 10)
        page = self.request.GET.get('page')

        try:
            original_list = album_list_paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            original_list = album_list_paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page of results.
            original_list = album_list_paginator.page(album_list_paginator.num_pages)

        # Manipulate user's album list after getting only album and score field.
        context['intersection_list'] = make_album_list(original_list, self.request.user)
        context['intersection_list_page'] = original_list

        context['intersection_count'] = len(user_album_list)

        context['pages'] = album_list_paginator.page_range

        return context


class UserCreateView(CreateView):
    """
    User creation form.
    """
    template_name = 'users/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('user:create_done')


class UserCreateDoneTV(TemplateView):
    """
    After creating a user, redirect to 'register done' page.
    """
    template_name = 'users/register_done.html'


class UserDetailView(LoginRequiredMixin, DetailView):
    """
    User's profile.
    """
    template_name = 'users/user_main.html'
    model = MmUser

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)

        # Get many-to-many field list.
        user_album_list = self.object.mmuseralbum_set.all()

        # Pagination for user_album_list (for 10 albums)
        album_list_paginator = Paginator(user_album_list, 10)
        page = self.request.GET.get('page')

        try:
            original_list = album_list_paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            original_list = album_list_paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page of results.
            original_list = album_list_paginator.page(album_list_paginator.num_pages)

        # Manipulate user's album list after getting only album and score field.
        album_score_list = original_list.object_list.only("album", "score")
        context['user_object_list'] = make_user_album_list(album_score_list, self.object, self.request.user)
        context['user_album_list'] = original_list

        # Get count of intersection for user's albums between certain user and user logged in.
        if self.object != self.request.user:
            context['intersection_count'] = len(get_album_intersection_two_users(self.object, self.request.user))

        context['pages'] = album_list_paginator.page_range
        context['user_album_count'] = self.object.albums.count()

        return context


class UserMainView(UserDetailView):
    """
    View to see current user's profile
    """

    # Get current user without primary key.
    def get_object(self, queryset=None):
        return self.request.user


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """
    Modify user's profile.
    """
    form_class = UserChangeForm
    template_name = 'users/modify.html'
    success_url = reverse_lazy('user:main')

    # Get current user without primary key.
    def get_object(self, queryset=None):
        return self.request.user


class UserDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete user.
    """
    model = MmUser
    success_url = reverse_lazy('index')
    template_name = 'users/user_confirm_delete.html'

    # Get current user without primary key.
    def get_object(self, queryset=None):
        return self.request.user

    # Reduce album owners count.
    def delete(self, request, *args, **kwargs):
        # Get album list.
        albums = self.get_object().albums.all()

        # Reduce album owner count for all albums.
        for album in albums:
            if album.owner_count > 0:
                album.owner_count -= 1
                album.save()

        return super(UserDeleteView, self).delete(request, *args, **kwargs)


class UserAlbumAddConfirmView(LoginRequiredMixin, DetailView):
    """
    Confirm before adding an album to user's album list.
    """
    model = Album
    template_name = 'users/user_add_album.html'

    def get_context_data(self, **kwargs):
        context = super(UserAlbumAddConfirmView, self).get_context_data(**kwargs)
        context['object'] = make_album_info(self.object, self.object.album_cover_file.url)
        return context


class UserAlbumAddView(LoginRequiredMixin, View):
    """
    Add album to user's album list.
    """
    def post(self, request, *args, **kwargs):
        # Get album data
        album_to_add = get_object_or_404(Album, pk=request.POST['album_id'])
        album_owner = request.user

        # If duplicated item exists, don't save.
        if MmUserAlbum.objects.filter(Q(user=album_owner) & Q(album=album_to_add)).count() != 0:
            return redirect('user:main')

        # Save item.
        mm_user_album = MmUserAlbum(user=album_owner, album=album_to_add)
        mm_user_album.save()

        # Add album owners count.
        album_to_add.owner_count += 1
        album_to_add.save()

        return redirect('user:main')


class UserAlbumDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete album from user's album list.
    """
    model = MmUserAlbum
    template_name = 'users/user_delete_album.html'
    success_url = reverse_lazy('user:main')

    def get_context_data(self, **kwargs):
        context = super(UserAlbumDeleteView, self).get_context_data(**kwargs)
        context['album'] = make_album_info(self.object.album, self.object.album.album_cover_file.url)
        return context

    def delete(self, request, *args, **kwargs):
        album_to_delete = self.get_object().album

        # Reduce album owners count.
        if album_to_delete.owner_count > 0:
            album_to_delete.owner_count -= 1

        # Calculate average rating again without self.object
        album_avg = MmUserAlbum.objects.filter(Q(album=album_to_delete)
                                               & ~Q(user=request.user)).aggregate(Avg('score'))['score__avg']
        if album_avg is not None:
            album_to_delete.average_rating = float(album_avg)
        else:
            album_to_delete.average_rating = None

        album_to_delete.save()
        return super(UserAlbumDeleteView, self).delete(request, *args, **kwargs)


class UserAlbumRatingView(LoginRequiredMixin, View):
    """
    Rating album from user's album list.
    """

    def post(self, request, *args, **kwargs):
        # Get MmUserAlbum object.
        user_album = get_object_or_404(MmUserAlbum, pk=request.POST['user_album_id'])

        # Update score for an album.
        user_album.score = int(request.POST['score'])
        user_album.save()

        # Calculate average score and save.
        album = user_album.album
        album_avg = MmUserAlbum.objects.filter(Q(album=album)).aggregate(Avg('score'))['score__avg']

        if album_avg is not None:
            album.average_rating = float(album_avg)
            album.save()

        return redirect('user:main')


class UserAbnormalRequestRV(LoginRequiredMixin, RedirectView):
    """
    If the app get abnormal url, just redirect to user's main page.
    """
    url = reverse_lazy('user:main')


class UserAlbumSearchFV(LoginRequiredMixin, FormView):
    """
    Search albums from user's album list. (by Artist/Album title)
    """
    form_class = AlbumSearchForm
    template_name = "users/user_album_search.html"

    def form_valid(self, form):
        search_type = self.request.POST["search_type"]
        keyword = self.request.POST["keyword"]
        # Search album from database.
        if search_type == "artist":
            result = self.request.user.albums.filter(album_artist__icontains=keyword)
        elif search_type == "album":
            result = self.request.user.albums.filter(album_title__icontains=keyword)
        else:
            result = []

        context = dict()
        context['form'] = form
        context['search_type'] = search_type
        context['keyword'] = keyword
        context['object_list'] = make_album_list(result, self.request.user)

        return render(self.request, self.template_name, context)
