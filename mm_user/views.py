from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateView, View, RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.urlresolvers import reverse_lazy

from django.db.models import Q, Avg

from manager_core.models import Album

from mm_user.forms import UserCreationForm, UserChangeForm
from mm_user.models import MmUser, MmUserAlbum


# User creation form.
class UserCreateView(CreateView):
    template_name = 'users/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('user:create_done')


# After creating a user, redirect to 'register done' page.
class UserCreateDoneTV(TemplateView):
    template_name = 'users/register_done.html'


class UserDetailView(ListView):
    paginate_by = 10
    template_name = 'users/user_main.html'
    model = MmUserAlbum

    def get_context_data(self, **kwargs):
        return super(UserDetailView, self).get_context_data(**kwargs)


# View to see current user's profile
class UserMainView(LoginRequiredMixin, UserDetailView):
    paginate_by = 10
    template_name = 'users/user_main.html'

    def get_queryset(self):
        user = self.request.user
        user_queryset = MmUserAlbum.objects.filter(Q(user=user))
        return user_queryset

    def get_context_data(self, **kwargs):
        context = super(UserMainView, self).get_context_data(**kwargs)
        context['user_album_count'] = self.get_queryset().count()
        context['scores_list'] = range(1, 11)
        return context


# Modify user's profile.
class UserUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserChangeForm
    template_name = 'users/modify.html'
    success_url = reverse_lazy('user:main')

    # Get current user.
    def get_object(self):
        return self.request.user


# Delete user.
class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = MmUser
    success_url = reverse_lazy('manager_core:index')
    template_name = 'users/user_confirm_delete.html'

    # Get current user.
    def get_object(self):
        return self.request.user

    # Reduce album owners count.
    def delete(self, request, *args, **kwargs):
        # Get album list.
        albums = self.request.user.albums.all()

        # Reduce album owner count for all albums.
        for album in albums:
            if album.owner_count > 0:
                album.owner_count -= 1
                album.save()

        return super(UserDeleteView, self).delete(request, *args, **kwargs)


# Confirm before adding an album to user's album list.
class UserAlbumAddConfirmView(LoginRequiredMixin, DetailView):
    model = Album
    template_name = 'users/user_add_album.html'


# Add album to user's album list.
class UserAlbumAddView(LoginRequiredMixin, View):
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


# Delete album from user's album list.
class UserAlbumDeleteView(LoginRequiredMixin, DeleteView):
    model = MmUserAlbum
    template_name = 'users/user_delete_album.html'
    success_url = reverse_lazy('user:main')

    # Overriding delete method.
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


# Rating album from user's album list.
class UserAlbumRatingView(LoginRequiredMixin, View):

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


# If the app get abnormal url, just redirect to user's main page.
class UserAbnormalRequestRV(LoginRequiredMixin, RedirectView):
    url = reverse_lazy('user:main')
