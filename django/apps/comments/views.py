from django.contrib import messages as msg
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView, ProcessFormView

from notes.models import Note
from reports.views import ReportModelView
from users.decorators import login_required_view
from votes.views import VoteView
from zones.decorators import moderator_required_view
from .forms import CommentCreateForm, CommentReplyForm
from .models import Comment


# User views

@login_required_view
class CommentCreateView(FormView):
    form_class = CommentCreateForm
    template_name = 'comments/submit_page.html'

    def get_commented(self, *args, **kwargs):
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        context = super(CommentCreateView, self).get_context_data(**kwargs)
        context['commented_description'] = unicode(self.get_commented())
        return context

    def form_valid(self, form):
        author = self.request.user
        text = form.cleaned_data.get('note')
        item = self.get_commented()
        comment = form.save(commit=False)
        comment.note = Note.objects.create(text=text, author=author)
        comment.item = item
        comment.save()
        comment.cast_vote(user=author, way='up')
        comment.item.update_comment_count()
        comment.item.save()
        msg.add_message(self.request, msg.SUCCESS, _('Comment saved.'))
        return HttpResponseRedirect(comment.get_absolute_url())

    def form_invalid(self, form):
        msg.add_message(self.request, msg.ERROR, _('Not saved.'))
        return super(CommentCreateView, self).form_invalid(form)


@login_required_view
class CommentReplyView(SingleObjectMixin, FormView):
    model = Comment
    form_class = CommentReplyForm
    template_name = 'comments/submit_page.html'

    def get_context_data(self, **kwargs):
        context = super(CommentReplyView, self).get_context_data(**kwargs)
        context['commented_description'] = unicode(self.object.item)
        context['reply_to'] = self.object
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(CommentReplyView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(CommentReplyView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        author = self.request.user
        text = form.cleaned_data.get('note')
        parent = self.object
        reply = form.save(commit=False)
        reply.parent = parent
        reply.note = Note.objects.create(text=text, author=author)
        reply.item = parent.item
        reply.save()
        reply.cast_vote(user=author, way='up')
        reply.item.update_comment_count()
        reply.item.save()
        msg.add_message(self.request, msg.SUCCESS, _('Comment saved.'))
        return HttpResponseRedirect(reply.get_absolute_url())

    def form_invalid(self, form):
        msg.add_message(self.request, msg.ERROR, _('Not saved.'))
        return super(CommentReplyView, self).form_invalid(form)


@login_required_view
class CommentVoteView(VoteView):
    model = Comment


@login_required_view
class CommentReportView(ReportModelView):
    model = Comment


# Moderator views*

@moderator_required_view
class CommentEvaluateView(SingleObjectMixin, ProcessFormView):
    model = Comment

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
            self.object.item.show()
            msg.add_message(self.request, msg.SUCCESS, _("Made public."))
        elif value == 'hidden':
            self.object.item.hide()
            msg.add_message(self.request, msg.SUCCESS, _("Made private."))
        else:
            return HttpResponseBadRequest(_("Invalid data."))
        return HttpResponseRedirect(self.object.get_absolute_url())
