import json

from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    )
from django.utils.translation import ugettext as _
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin


class VoteView(SingleObjectMixin, View):
    """Add or update vote. POST only."""
    model = None

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        way = request.POST.get('vote')
        if way not in ('up', 'down'):
            return HttpResponseBadRequest(_("Invalid data."))
        self.object = self.get_object()
        vote = self.object.cast_vote(request.user, way)
        if request.is_ajax():
            return HttpResponse(
                json.dumps({'status': vote.get_description()}),
                content_type='application/json',
                )
        else:
            return HttpResponseRedirect(self.object.get_absolute_url())
