from django.views.generic.base import TemplateView

from django.views.generic.edit import CreateView
from mm_user.forms import UserCreationForm
from django.core.urlresolvers import reverse_lazy


class UserCreateView(CreateView):
    template_name = 'users/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('user:create_done')


class UserCreateDoneTV(TemplateView):
    template_name = 'users/register_done.html'
