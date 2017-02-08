from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.urlresolvers import reverse_lazy

from mm_user.forms import UserCreationForm, UserChangeForm
from mm_user.models import MmUser


# User creation form.
class UserCreateView(CreateView):
    template_name = 'users/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('user:create_done')


# After creating a user, redirect to 'register done' page.
class UserCreateDoneTV(TemplateView):
    template_name = 'users/register_done.html'


# View to see user's profile
class UserDetailView(DetailView):
    model = MmUser
    template_name = 'users/user_main.html'

    def get_context_data(self, **kwargs):
        return super(UserDetailView, self).get_context_data(**kwargs)


# View to see current user's profile
class UserMainView(LoginRequiredMixin, UserDetailView):
    model = MmUser
    template_name = 'users/user_main.html'

    # Get current user.
    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        return super(UserMainView, self).get_context_data(**kwargs)


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


# Change password for current user.
class ChangePasswordView(LoginRequiredMixin, UpdateView):
    pass
