from django.contrib import messages as msg
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.core.urlresolvers import reverse
from django.forms.util import ErrorList
from django.http import Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from django.views.generic.base import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import FormView, ProcessFormView
from django.views.generic.list import ListView

from misc.mixins import OrderedItemListMixin, NavigationMixin
from reports.views import ReportModelView
from submissions.models import Submission
from .decorators import admin_required_view, login_required_view
from .forms import RegisterForm, LoginForm, EraseForm, PasswordForm


class ProfileNavigationMixin(NavigationMixin):

    def get_navigation(self):
        navigation = super(ProfileNavigationMixin, self).get_navigation()
        navigation[_("Profile")] = self.object.get_about_url()
        navigation[_("Submissions")] = self.object.get_submitted_url()
        navigation[_("Subscriptions")] = self.object.get_subscribed_url()
        return navigation


class AccountNavigationMixin(NavigationMixin):

    def get_navigation(self):
        navigation = super(AccountNavigationMixin, self).get_navigation()
        navigation[_("Password")] = reverse('account:password')
        navigation[_("Erase")] = reverse('account:erase')
        return navigation


# Public views

class ProfileBaseView(ProfileNavigationMixin, DetailView):
    model = get_user_model()
    slug_field = 'username'
    context_object_name = 'current_profile'


class ProfileAboutView(ProfileBaseView):
    section = _("Profile")
    template_name = 'users/profiles/about_page.html'


class ProfileSubscribedView(OrderedItemListMixin, ProfileBaseView):
    section = _("Subscriptions")
    template_name = 'users/profiles/subscribed_page.html'
    context_item_list_name = 'submission_list'
    default_order = 'global'

    def get_context_data(self, **kwargs):
        context = super(ProfileSubscribedView, self).get_context_data(**kwargs)
        context['zone_list'] = self.object.subscribed_zone_set.all()
        return context

    def get_ordered_list(self, order, **kwargs):
        submissions = Submission.objects.from_subscriptions(
            user=self.request.user,
            order=order,
            subscriber=self.object,
            is_rejected=False,
            ).select_related('zone', 'author')
        return submissions


class ProfileSubmittedView(ProfileSubscribedView):
    section = _("Submissions")
    template_name = 'users/profiles/submitted_page.html'

    def get_ordered_list(self, order, **kwargs):
        submissions = self.object.submission_set.custom(
            user=self.request.user,
            order=order,
            ).select_related('zone', 'author')
        return submissions


class AccountRegisterView(FormView):
    form_class = RegisterForm
    template_name = 'users/account/register_page.html'
    success_url = '/'

    def form_valid(self, form):
        # Register new user
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        User = get_user_model()
        User.objects.create_user(username=username, password=password)
        # Authenticate and login the current request
        if self.request.user.is_authenticated():
            logout(self.request)
            message = _("Current user logued out.")
            msg.add_message(self.request, msg.WARNING, message)
        user = authenticate(username=username, password=password)
        login(self.request, user)
        message = _("New account created. Welcome.")
        msg.add_message(self.request, msg.SUCCESS, message)
        return super(AccountRegisterView, self).form_valid(form)


class AccountLoginView(FormView):
    form_class = LoginForm
    template_name = 'users/account/login_page.html'
    success_url = '/'

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return super(AccountLoginView, self).form_valid(form)


# User views

@login_required_view
class ProfileReportView(ReportModelView):
    slug_field = 'username'
    model = get_user_model()


@login_required_view
class AccountLogoutView(View):

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        if (request.user.is_authenticated):
            logout(request)
            msg.add_message(self.request, msg.SUCCESS, _("Goodbye."))
        return HttpResponseRedirect('/')


@login_required_view
class AccountSubscribedView(NavigationMixin, OrderedItemListMixin, TemplateView):
    template_name = 'users/account/subscribed_page.html'
    context_item_list_name = 'submission_list'
    default_order = 'global'

    def get_context_data(self, **kwargs):
        context = super(AccountSubscribedView, self).get_context_data(**kwargs)
        context['zone_list'] = self.request.user.subscribed_zone_set.all()
        return context

    def get_ordered_list(self, order, **kwargs):
        submissions = Submission.objects.from_subscriptions(
            user=self.request.user,
            order=order,
            subscriber=self.request.user,
            is_rejected=False,
            ).select_related('zone', 'author')
        return submissions

    def get_action(self):
        return (
            _("Share"),
            reverse('submissions:create') + '?filter=subscriptions'
            )


@login_required_view
class AccountEraseView(AccountNavigationMixin, FormView):
    form_class = EraseForm
    template_name = 'users/account/erase_page.html'
    success_url = '/'
    section = _("Erase")

    def form_valid(self, form):
        user = self.request.user
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        if username == user.username:
            if user.check_password(password):
                user.erase()
                logout(self.request)
                msg.add_message(self.request, msg.SUCCESS, _("User deleted."))
                return super(AccountEraseView, self).form_valid(form)
            else:
                form._errors['password'] = ErrorList([_("Wrong password")])
                return super(AccountEraseView, self).form_invalid(form)
        else:
            form._errors['username'] = ErrorList([_("Wrong username")])
            return super(AccountEraseView, self).form_invalid(form)


@login_required_view
class AccountPasswordView(AccountNavigationMixin, FormView):
    section = _("Password")
    form_class = PasswordForm
    template_name = 'users/account/password_page.html'
    success_url = '/'

    def form_valid(self, form):
        user = self.request.user
        password = form.cleaned_data['password']
        new_password = form.cleaned_data['new_password_1']
        if user.check_password(password):
            user.set_password(new_password)
            user.save()
            msg.add_message(self.request, msg.SUCCESS, _("Updated."))
            return super(AccountPasswordView, self).form_valid(form)
        else:
            form._errors['password'] = ErrorList([_("Wrong password")])
            return super(AccountPasswordView, self).form_invalid(form)


# Admin views

@admin_required_view
class ProfileIndexView(ListView):
    model = get_user_model()
    template_name = 'users/profiles/index_page.html'


@admin_required_view
class ProfileEvaluateView(SingleObjectMixin, ProcessFormView):
    model = get_user_model()
    slug_field = 'username'

    def post(self, request, *args, **kwargs):
        value = request.POST.get('evaluation')
        self.object = self.get_object()
        if value == 'ban':
            self.object.ban()
            msg.add_message(self.request, msg.SUCCESS, _("Banned."))
        elif value == 'allow':
            self.object.allow()
            msg.add_message(self.request, msg.SUCCESS, _("Allowed."))
        elif value == 'reject':
            self.object.reject()
            msg.add_message(self.request, msg.SUCCESS, _("Rejected."))
        else:
            return HttpResponseBadRequest(_("Invalid data."))
        return HttpResponseRedirect(self.object.get_absolute_url())
