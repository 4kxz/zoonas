from django.conf.urls import patterns, url

from .views import DomainIndexView


urlpatterns = patterns(
    '',
    url(
        r'^$',
        DomainIndexView.as_view(),
        name='index',
        ),
    )
