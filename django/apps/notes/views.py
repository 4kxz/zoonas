from django.conf import settings
from django.contrib import messages as msg
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from misc.decorators import author_required_view
from users.decorators import admin_required_view, login_required_view
from .models import Note
from .forms import NoteEditForm, NoteEraseForm


# User views

@login_required_view
class NoteMainView(DetailView):
    model = Note
    template_name = 'notes/main_page.html'


# Author views

@author_required_view
class NoteEditView(UpdateView):
    model = Note
    template_name = 'notes/edit_page.html'
    form_class = NoteEditForm

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.is_editable:
            raise PermissionDenied
        return super(NoteEditView, self).post(request, *args, **kwargs)


@author_required_view
class NoteEraseView(UpdateView):
    """Allows the author to erase a note."""
    model = Note
    template_name = 'notes/erase_page.html'
    form_class = NoteEraseForm

    def get_context_data(self, **kwargs):
        context = super(NoteEraseView, self).get_context_data(**kwargs)
        context['form'] = NoteEraseForm()
        return context

    def post(self, request, *args, **kwargs):
        note = self.get_object()
        note.erase()
        msg.add_message(self.request, msg.SUCCESS, _('Erased.'))
        return HttpResponseRedirect(note.get_absolute_url())


# Admin views

@admin_required_view
class NoteIndexView(ListView):
    model = Note
    template_name = 'notes/index_page.html'
    paginate_by = settings.SUBMISSIONS_PER_PAGE
