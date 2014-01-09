from django.conf import settings
from django.contrib import messages as msg
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, ProcessFormView
from django.views.generic.list import ListView

from comments.views import CommentCreateView
from misc.decorators import author_required_view
from misc.mixins import NavigationMixin, OrderedMixin
from reports.views import ReportModelView
from users.decorators import login_required_view
from votes.views import VoteView
from zones.decorators import moderator_required_view
from zones.mixins import ZoneMixin
from .decorators import author_or_moderator_required_view
from .models import Submission
from .forms import (
    SubmissionCreateForm,
    SubmissionEraseForm,
    SubmissionUpdateForm,
    )


# Public views

class SubmissionMainView(ZoneMixin, DetailView):
    """Displays a single Submission details and options."""
    model = Submission
    template_name = 'submissions/main_page.html'

    def get_subsection(self):
        return (self.object.title, self.object.get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super(SubmissionMainView, self).get_context_data(**kwargs)
        context['is_old'] = self.object.is_older_than(settings.EDIT_TIME)
        comment_form = CommentCreateView.form_class
        comment_url = self.object.get_comment_url()
        context['comment_form'] = comment_form(action=comment_url)
        return context


class SubmissionListView(NavigationMixin, OrderedMixin, ListView):
    """Lists all submissions."""
    model = Submission
    template_name = 'submissions/index_page.html'
    paginate_by = settings.SUBMISSIONS_PER_PAGE
    default_order = 'global'

    def get_queryset(self):
        submissions = Submission.objects.custom(
            user=self.request.user,
            order=self.get_order(),
            is_rejected=False,
        ).select_related('zone', 'author')
        return submissions

    def get_action(self):
        return (_("Share"), reverse('submissions:create'))


# User views

@login_required_view
class SubmissionCreateView(CreateView):
    """Submission creation."""
    model = Submission
    form_class = SubmissionCreateForm
    template_name = 'submissions/create_page.html'

    def get_form_kwargs(self):
        kwargs = super(SubmissionCreateView, self).get_form_kwargs()
        if self.request.GET.get('filter') == 'subscriptions':
            kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        submission = form.save(commit=False)
        submission.author = self.request.user
        submission.save()
        return super(SubmissionCreateView, self).form_valid(form)


@login_required_view
class SubmissionVoteView(VoteView):
    model = Submission


@login_required_view
class SubmissionCommentView(SingleObjectMixin, CommentCreateView):
    """Submit a comment."""
    model = Submission

    def get_commented(self):
        return self.object

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(SubmissionCommentView, self).get(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        return super(SubmissionCommentView, self).post(*args, **kwargs)


@login_required_view
class SubmissionReportView(ReportModelView):
    model = Submission


# Author views

@author_or_moderator_required_view
class SubmissionUpdateView(UpdateView):
    """Edit a submission.
    Allows the author to edit the submission during `edit_time` minutes.
    Allows moderators and admins to edit the submission.
    """
    model = Submission
    form_class = SubmissionUpdateForm
    template_name = 'submissions/update_page.html'

    def dispatch(self, req, *args, **kwargs):
        """Checks that the user can still edit the submission."""
        submission = self.get_object()
        if (
            not req.user.is_superuser and
            submission.is_author(req.user) and
            submission.is_older_than(settings.EDIT_TIME) and
            not submission.zone.is_moderator(req.user)
        ):
            message = _('You can only edit the first {} minutes.')
            message = message.format(settings.EDIT_TIME / 60)
            msg.add_message(self.request, msg.ERROR, message)
            raise PermissionDenied
        return super(SubmissionUpdateView, self).dispatch(req, *args, **kwargs)

    def form_valid(self, form):
        msg.add_message(self.request, msg.SUCCESS, _('Updated.'))
        return super(SubmissionUpdateView, self).form_valid(form)

    def form_invalid(self, form):
        msg.add_message(self.request, msg.ERROR, _('Invalid data.'))
        return super(SubmissionUpdateView, self).form_invalid(form)


@author_required_view
class SubmissionEraseView(UpdateView):
    """Allows the author or a moderator to erase a submission."""
    model = Submission
    template_name = 'submissions/erase_page.html'
    form_class = SubmissionEraseForm

    def get_context_data(self, **kwargs):
        context = super(SubmissionEraseView, self).get_context_data(**kwargs)
        context['form'] = SubmissionEraseForm()
        return context

    def post(self, request, *args, **kwargs):
        submission = self.get_object()
        submission.erase()
        msg.add_message(self.request, msg.SUCCESS, _('Erased.'))
        return HttpResponseRedirect(submission.get_absolute_url())


# Moderator views

@moderator_required_view
class SubmissionEvaluateView(SingleObjectMixin, ProcessFormView):
    model = Submission

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        value = request.POST.get('evaluation')
        self.object = self.get_object()
        if value == 'allow':
            self.object.allow()
            msg.add_message(self.request, msg.SUCCESS, _("Allowed."))
        elif value == 'reject':
            self.object.reject()
            msg.add_message(self.request, msg.SUCCESS, _("Rejected."))
        elif value == 'public':
            self.object.show()
            msg.add_message(self.request, msg.SUCCESS, _("Made public."))
        elif value == 'hidden':
            self.object.hide()
            msg.add_message(self.request, msg.SUCCESS, _("Made private."))
        else:
            return HttpResponseBadRequest(_("Invalid data."))
        return HttpResponseRedirect(self.object.get_absolute_url())
