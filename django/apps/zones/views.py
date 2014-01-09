from django.contrib import messages as msg
from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponseBadRequest
from django.utils.translation import ugettext as _
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import (
    CreateView,
    UpdateView,
    FormView,
    FormMixin,
    ProcessFormView
    )
from django.views.generic.list import ListView

from users.models import User
from users.decorators import login_required_view, admin_required_view
from misc.mixins import OrderedItemListMixin
from submissions.forms import ZoneSubmissionCreateForm
from votes.views import VoteView
from .decorators import moderator_required_view
from .mixins import ZoneMixin
from .models import Proposal, Zone
from .forms import (
    GrantPermissionForm,
    ProposalCreateForm,
    ZoneCreateForm,
    ZoneUpdateForm,
    )


# Public views

class IndexView(ListView):
    model = Zone
    template_name = 'zones/index_page.html'


class AboutView(ZoneMixin, DetailView):
    model = Zone
    template_name = 'zones/about_page.html'
    section = _("Zone")


class MainView(ZoneMixin, OrderedItemListMixin, DetailView):
    model = Zone
    template_name = 'zones/base_page.html'
    context_item_list_name = 'submission_list'
    default_order = 'zone'
    section = _("Frontpage")

    def get_ordered_list(self, order, **kwargs):
        submissions = self.object.submission_set.custom(
            user=self.request.user,
            order=order,
            is_rejected=False,
            ).select_related('zone', 'author')
        return submissions


# User views

@login_required_view
class SubmitView(ZoneMixin, SingleObjectMixin, FormView):
    """Create submission in the current zone."""
    model = Zone
    form_class = ZoneSubmissionCreateForm
    template_name = 'zones/submit_page.html'
    section = _("Share")

    def get_initial(self):
        initial = super(SubmitView, self).get_initial()
        initial['zone'] = self.object
        return initial

    def form_valid(self, form):
        submission = form.save(commit=False)
        submission.author = self.request.user
        submission.save()
        return HttpResponseRedirect(submission.get_absolute_url())

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(SubmitView, self).get(request, *args, **kwargs)


@login_required_view
class SubscriptionsView(SingleObjectMixin, FormMixin, ProcessFormView):
    """Subscribe or unsubscribe user to the current zone."""
    model = Zone

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        zone = self.object = self.get_object()
        user = request.user
        do = request.POST.get('subscription')
        if do == 'add':
            if user.subscription_count() < settings.SUBSCRIPTION_LIMIT:
                zone.subscribe(user)
                message = _("Added.")
                status = msg.SUCCESS
            else:
                message = _("Subscription limit exceeded.")
                status = msg.ERROR
        elif do == 'remove':
            zone.unsubscribe(user)
            message = _("Removed.")
            status = msg.SUCCESS
        else:
            return HttpResponseBadRequest()
        msg.add_message(request, status, message)
        return HttpResponseRedirect(zone.get_absolute_url())


@login_required_view
class ProposalCreateView(CreateView):
    model = Proposal
    form_class = ProposalCreateForm
    template_name = 'zones/propose_page.html'

    def form_valid(self, form):
        proposal = form.save(commit=False)
        proposal.author = self.request.user
        proposal.save()
        return super(ProposalCreateView, self).form_valid(form)


@login_required_view
class ProposalIndexView(ListView):
    model = Proposal
    template_name = 'zones/proposals_page.html'


@login_required_view
class ProposalVoteView(VoteView):
    model = Proposal


# Moderator views

@moderator_required_view
class SettingsView(ZoneMixin, UpdateView):
    """Display zone settings. Update zone information."""
    model = Zone
    form_class = ZoneUpdateForm
    template_name = 'zones/settings_page.html'
    section = _("Settings")

    def get_context_data(self, **kwargs):
        kwargs['add_form'] = GrantPermissionForm(self.object)
        return super(SettingsView, self).get_context_data(**kwargs)


@moderator_required_view
class PermissionsView(SingleObjectMixin, FormMixin, ProcessFormView):
    """Grant and revoke permissions."""
    model = Zone
    form_class = GrantPermissionForm

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.do = request.POST.get('permission')
        if self.do not in ('grant', 'revoke'):
            return HttpResponseBadRequest()
        return super(PermissionsView, self).post(request, *args, **kwargs)

    def get_form(self, form_class):
        return form_class(zone=self.get_object(), **self.get_form_kwargs())

    def form_valid(self, form):
        user = self.request.user
        zone = self.object
        username = form.cleaned_data.get('username')
        target = User.objects.filter(username=username)
        if not target.exists():
            message = _("{} not found.".format(username))
            msg.add_message(self.request, msg.ERROR, message)
        else:
            target = target.get()
            if self.do == 'grant':
                try:
                    zone.grant_permission(target=target, moderator=user)
                    status = msg.SUCCESS
                    message = _("Added.")
                except ValueError:
                    status = msg.ERROR
                    message = _(
                        "User could not be added. "
                        "Make sure you typed the right username. "
                        "Be aware that there is a limit of {} moderators. "
                        ).format(settings.MODERATOR_LIMIT)
            else:
                try:
                    zone.revoke_permission(target=target, moderator=user)
                    status = msg.SUCCESS
                    message = _("Revoked")
                except ValueError:
                    status = msg.ERROR
                    message = _(
                        "The moderator could not be removed. "
                        "Be aware that you can't remove older moderators. "
                        ).format(settings.MODERATOR_LIMIT)

            msg.add_message(self.request, status, message)
        return HttpResponseRedirect(zone.get_settings_url())

    def form_invalid(self, form):
        msg.add_message(self.request, msg.ERROR, _("Invalid data."))
        return HttpResponseRedirect(self.get_object().get_settings_url())


# Admin views

@admin_required_view
class ZoneCreateView(CreateView):
    model = Zone
    form_class = ZoneCreateForm
    template_name = 'zones/create_page.html'

    def form_valid(self, form):
        result = super(ZoneCreateView, self).form_valid(form)
        self.object.add_founder(self.request.user)
        msg.add_message(self.request, msg.SUCCESS, _('Created.'))
        return result
