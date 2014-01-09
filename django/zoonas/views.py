
from submissions.views import SubmissionListView
from users.views import AccountSubscribedView


def front_page_view(request, *args, **kwargs):
    if request.user.is_authenticated():
        return AccountSubscribedView.as_view()(request, *args, **kwargs)
    else:
        return SubmissionListView.as_view()(request, *args, **kwargs)
