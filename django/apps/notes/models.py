from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _

from misc.fields import AutoLastModifiedField
from misc.models import Author, Created, Erased, Private
from users.models import User


class Note(Author, Created, Erased, Private):
    """Just a piece of text with some attributes.
    Base building block for descriptions, comments, reports, submissions, etc.
    """
    text = models.CharField(
        max_length=settings.MESSAGE_LENGTH,
        )
    modified = AutoLastModifiedField()
    is_editable = models.BooleanField(
        editable=False,
        default=True,
        )

    class Meta:
        ordering = ['-modified']

    def save(self, **kwargs):
        if not self.is_editable:
            return super(Note, self).save(update_fields=['is_editable'])
        else:
            return super(Note, self).save(**kwargs)

    def erase(self, **kwargs):
        self.text = _("Erased text.")
        self.author = User.objects.get_default()
        return super(Note, self).erase(**kwargs)

    def __unicode__(self):
        return u"{}: {}".format(self.author, self.get_snippet())

    def get_snippet(self):
        return self.text[:150]

    def get_absolute_url(self):
        return reverse('notes:main', args=[self.pk])

    def get_edit_url(self):
        return reverse('notes:edit', args=[self.pk])

    def get_erase_url(self):
        return reverse('notes:erase', args=[self.pk])

