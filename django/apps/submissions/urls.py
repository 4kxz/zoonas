from django.conf.urls import patterns, url

from .views import (
    SubmissionCommentView,
    SubmissionCreateView,
    SubmissionEraseView,
    SubmissionEvaluateView,
    SubmissionListView,
    SubmissionMainView,
    SubmissionReportView,
    SubmissionUpdateView,
    SubmissionVoteView,
)


urlpatterns = patterns(
    '',
    url(
        r'^$',
        SubmissionListView.as_view(),
        name='global',
        ),
    url(
        r'^new/$',
        SubmissionCreateView.as_view(),
        name='create',
        ),
    url(
        r'^(?P<slug>[\w\d-]+)/$',
        SubmissionMainView.as_view(),
        name='details',
        ),
    url(
        r'^(?P<slug>[\w\d-]+)/vote/$',
        SubmissionVoteView.as_view(),
        name='vote',
        ),
    url(
        r'^(?P<slug>[\w\d-]+)/update/$',
        SubmissionUpdateView.as_view(),
        name='update',
        ),
    url(
        r'^(?P<slug>[\w\d-]+)/report/$',
        SubmissionReportView.as_view(),
        name='report',
        ),
    url(
        r'^(?P<slug>[\w\d-]+)/evaluate/$',
        SubmissionEvaluateView.as_view(),
        name='evaluate',
        ),
    url(
        r'^(?P<slug>[\w\d-]+)/erase/$',
        SubmissionEraseView.as_view(),
        name='erase',
        ),
    url(
        r'^(?P<slug>[\w\d-]+)/comment/$',
        SubmissionCommentView.as_view(),
        name='comment',
        ),
    )
