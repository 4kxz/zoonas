from django.conf.urls import patterns, url

from ..views import (
    AccountEraseView,
    AccountLoginView,
    AccountLogoutView,
    AccountPasswordView,
    AccountRegisterView,
    )


urlpatterns = patterns(
    '',
    url(
        r'^erase/$',
        AccountEraseView.as_view(),
        name='erase',
        ),
    url(
        r'^login/$',
        AccountLoginView.as_view(),
        name='login',
        ),
    url(
        r'^logout/$',
        AccountLogoutView.as_view(),
        name='logout',
        ),
    url(
        r'^password/$',
        AccountPasswordView.as_view(),
        name='password',
        ),
    url(
        r'^join/$',
        AccountRegisterView.as_view(),
        name='register',
        ),
    )
