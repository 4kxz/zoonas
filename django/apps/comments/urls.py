from django.conf.urls import patterns, url

from .views import (
    CommentEvaluateView,
    CommentReplyView,
    CommentReportView,
    CommentVoteView,
    )

urlpatterns = patterns(
    '',
    url(
        r'^(?P<pk>[0-9]+)/reply/$',
        CommentReplyView.as_view(),
        name='reply',
        ),
    url(
        r'^(?P<pk>[0-9]+)/evaluate/$',
        CommentEvaluateView.as_view(),
        name='evaluate',
        ),
    url(
        r'^(?P<pk>[0-9]+)/report/$',
        CommentReportView.as_view(),
        name='report',
        ),
    url(
        r'^(?P<pk>[0-9]+)/vote/$',
        CommentVoteView.as_view(),
        name='vote',
        ),
    )
