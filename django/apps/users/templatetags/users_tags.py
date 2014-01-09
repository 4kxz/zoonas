from django.template import Library

register = Library()


@register.filter
def is_moderator(user, zone):
    return zone.is_moderator(user)


@register.filter
def is_subscriber(user, zone):
    return zone.is_subscriber(user)


@register.inclusion_tag('users/name_link.html')
def username_link(user):
    return dict(user=user)
