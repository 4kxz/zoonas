from django.conf import settings
from django.conf.urls import include, patterns, url
from django.conf.urls.static import static
from django.views.generic.base import TemplateView

from .views import front_page_view

urlpatterns = patterns(
    '',
    url(
        r'^$',
        front_page_view,
        name='frontpage',
        ),
    url(
        r'^zones/',
        include('zones.urls', namespace='zones'),
        ),
    url(
        r'^submissions/',
        include('submissions.urls', namespace='submissions'),
        ),
    url(
        r'^users/',
        include('users.urls.profiles', namespace='profiles'),
        ),
    url(
        r'^account/',
        include('users.urls.account', namespace='account'),
        ),
    url(
        r'^notes/',
        include('notes.urls', namespace='notes'),
        ),
    url(
        r'^reports/',
        include('reports.urls', namespace='reports'),
        ),
    url(
        r'^comments/',
        include('comments.urls', namespace='comments'),
        ),
    url(
        r'^domains/',
        include('domains.urls', namespace='domains'),
        ),
    url(
        r'^help/faq/$',
        TemplateView.as_view(template_name='help/faq_page.html'),
        name='faq',
        ),
    url(
        r'^help/rules/$',
        TemplateView.as_view(template_name='help/rules_page.html'),
        name='rules',
        ),
    ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # FIXME: Used in localhost, find a way to move it to settings/development
