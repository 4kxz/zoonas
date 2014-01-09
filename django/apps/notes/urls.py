from django.conf.urls import patterns, url

from .views import NoteEditView, NoteEraseView, NoteIndexView, NoteMainView


urlpatterns = patterns(
    '',
    url(
        r'^$',
        NoteIndexView.as_view(),
        name='index',
        ),
    url(
        r'^(?P<pk>[0-9]+)/$',
        NoteMainView.as_view(),
        name='main',
        ),
    url(
        r'^(?P<pk>[0-9]+)/edit/$',
        NoteEditView.as_view(),
        name='edit',
        ),
    url(
        r'^(?P<pk>[0-9]+)/erase/$',
        NoteEraseView.as_view(),
        name='erase',
        ),
    )
