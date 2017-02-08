from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView

from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.urlresolvers import reverse_lazy

from mm_user.forms import UserCreationForm
from mm_user.models import MmUser


class UserCreateView(CreateView):
    template_name = 'users/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('user:create_done')


class UserCreateDoneTV(TemplateView):
    template_name = 'users/register_done.html'


class UserDetailView(DetailView):
    model = MmUser
    template_name = 'users/user_main.html'

    def get_context_data(self, **kwargs):
        return super(UserDetailView, self).get_context_data(**kwargs)


class UserMainView(LoginRequiredMixin, UserDetailView):
    model = MmUser
    template_name = 'users/user_main.html'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        return super(UserMainView, self).get_context_data(**kwargs)

