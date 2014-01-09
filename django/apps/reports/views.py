from django.conf import settings
from django.contrib import messages as msg
from django.http import Http404, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import UpdateView, FormView
from django.views.generic.list import ListView

from notes.models import Note
from users.decorators import admin_required_view, login_required_view
from .models import Report
from .forms import ReportCreateForm


# User views

@login_required_view
class ReportCreateView(FormView):
    template_name = 'reports/submit_page.html'
    form_class = ReportCreateForm

    def get_reported(self):
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        context = super(ReportCreateView, self).get_context_data(**kwargs)
        context['reported_description'] = self.get_reported()
        return context

    def form_valid(self, form):
        author = self.request.user
        item = self.get_reported()
        text = form.cleaned_data.get('note')
        report = form.save(commit=False)
        report.note = Note.objects.create(text=text, author=author)
        report.item = item
        report.save()
        msg.add_message(self.request, msg.SUCCESS, _('Report saved.'))
        return HttpResponseRedirect(report.note.get_absolute_url())

    def form_invalid(self, form):
        msg.add_message(self.request, msg.ERROR, _('Not saved.'))
        return super(ReportCreateView, self).form_invalid(form)


@login_required_view
class ReportModelView(SingleObjectMixin, ReportCreateView):

    def get_reported(self):
        return self.object

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(ReportModelView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(ReportModelView, self).post(request, *args, **kwargs)


# Admin views

@admin_required_view
class ReportIndexView(ListView):
    model = Report
    template_name = 'reports/index_page.html'
    paginate_by = settings.SUBMISSIONS_PER_PAGE

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.unresolved()

    def get_context_data(self, *args, **kw):
        context = super(ReportIndexView, self).get_context_data(*args, **kw)
        context['unresolved_count'] = self.model.objects.unresolved().count()
        return context


@admin_required_view
class ReportResolveView(UpdateView):
    model = Report

    def get(self, request, *args, **kwargs):
        return Http404

    def post(self, form, *args, **kwargs):
        report = self.get_object()
        report.resolve()
        msg.add_message(self.request, msg.SUCCESS, _('Resolved.'))
        # TODO: Redirect to report url (there is no such thing yet)
        return HttpResponseRedirect(report.note.get_absolute_url())
