from django.conf import settings
from django.template import Library
from django.utils.html import escape
from django.utils.safestring import mark_safe

from misc.utils import attribute_string

register = Library()


@register.inclusion_tag('submissions/thumbnail.html')
def show_thumbnail(submission):
    """Displays a thumbnail image inside a div."""
    url = submission.get_thumbnail_url()
    return dict(thumbnail=url, link=submission.link, alt=submission.title)


@register.filter
def a(submission, cls=''):
    """Saves typing when writing submission links."""
    attr = {
        'href': escape(submission.link),
        'rel': 'nofollow',
        'target': '_blank',
        'class': cls,
        }
    return mark_safe(attribute_string(attr))


@register.filter
def article(submission, cls=''):
    """Saves typing when writing submission classes."""
    attr = {'class': cls + ' submission'}
    attr['class'] += ' private' if submission.is_private else ' public'
    if submission.is_older_than(settings.EDIT_TIME):
        attr['class'] += ' erased' if submission.is_erased else ' valid'
        attr['class'] += ' rejected' if submission.is_rejected else ' allowed'
    return mark_safe(attribute_string(attr))
