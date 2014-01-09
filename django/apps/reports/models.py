from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.core.urlresolvers import reverse
from django.db import models

from misc.models import Erased


class ReportManager(models.Manager):

    def unresolved(self):
        return self.filter(is_erased=False)


class Report(Erased):
    note = models.ForeignKey(
        editable=False,
        to='notes.Note',
        )
    item_content_type = models.ForeignKey(
        editable=False,
        to=ContentType,
        )
    item_id = models.PositiveIntegerField(
        editable=False,
        )
    item = GenericForeignKey(
        'item_content_type',
        'item_id',
        )
    is_important = models.BooleanField(
        editable=False,
        default=True,
        )
    objects = ReportManager()

    class Meta:
        ordering = ['is_erased', '-note__modified']

    def save(self, **kwargs):
        if self.id is None:
            try:
                self.is_private = self.item.is_private
            except AttributeError:
                pass
        return super(Report, self).save(**kwargs)

    def resolve(self):
        self.is_erased = True
        self.note.is_editable = False
        self.note.save()
        self.save()

    def __unicode__(self):
        return unicode(self.note)

    def get_absolute_url(self):
        return reverse('reports:index')

    def get_resolve_url(self):
        return reverse('reports:resolve', args=[self.id])
