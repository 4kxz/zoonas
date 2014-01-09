from django.conf.urls import patterns, url

from .views import ReportIndexView, ReportResolveView


urlpatterns = patterns(
    '',
    url(
        r'^$',
        ReportIndexView.as_view(),
        name='index',
        ),
    url(
        r'^(?P<pk>\d+)/resolve/$',
        ReportResolveView.as_view(),
        name='resolve',
        ),
    )
