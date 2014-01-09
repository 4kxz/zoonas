from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey

from misc.fields import AutoCreatedField


class LogEntry(models.Model):
    """Keeps track of user actions."""
    datetime = AutoCreatedField()
    user = models.ForeignKey(
        to='users.User',
        )
    item_content_type = models.ForeignKey(ContentType)
    item_id = models.PositiveIntegerField()
    item = GenericForeignKey(
        'item_content_type',
        'item_id',
        )
    description = models.CharField(
        max_length=256,
        )

    class Meta:
        ordering = ['-datetime']
