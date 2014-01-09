from django.conf.urls import patterns, url

from ..views import (
    ProfileAboutView,
    ProfileEvaluateView,
    ProfileReportView,
    ProfileSubmittedView,
    ProfileSubscribedView,
    ProfileIndexView,
)


urlpatterns = patterns(
    '',
    url(
        r'^$',
        ProfileIndexView.as_view(),
        name='index',
        ),
    url(
        r'^(?P<slug>[\w\d-]+)/$',
        ProfileAboutView.as_view(),
        name='about',
        ),
    url(
        r'^(?P<slug>[\w\d-]+)/evaluate/$',
        ProfileEvaluateView.as_view(),
        name='evaluate',
        ),
    url(
        r'^(?P<slug>[\w\d-]+)/report/$',
        ProfileReportView.as_view(),
        name='report',
        ),
    url(
        r'^(?P<slug>[\w\d-]+)/submitted/$',
        ProfileSubmittedView.as_view(),
        name='submitted',
        ),
    url(
        r'^(?P<slug>[\w\d-]+)/subscribed/$',
        ProfileSubscribedView.as_view(),
        name='subscribed',
        ),
    )
