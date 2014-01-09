from django.conf import settings
from django.template import Library
from django.utils.html import escape
from django.utils.safestring import mark_safe

from misc.utils import attribute_string

register = Library()


@register.filter
def article(comment, cls=''):
    """Saves typing when writing comment tags."""
    attr = {
        'id': "comment-{}".format(comment.pk),
        'class': cls + ' comment',
        }
    attr['class'] += ' private' if comment.note.is_private else ' public'
    attr['class'] += ' erased' if comment.note.is_erased else ' valid'
    attr['class'] += ' rejected' if comment.is_rejected else ' allowed'
    if comment.parent is not None:
        attr['data-parent'] = "comment-{}".format(comment.parent.pk)
    return mark_safe(attribute_string(attr))
