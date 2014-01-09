from django.db import models
from django.utils import timezone

from misc.fields import AutoCreatedField


class Author(models.Model):
    author = models.ForeignKey(
        editable=False,
        to='users.User',
    )

    class Meta:
        abstract = True

    def is_author(self, user):
        return user == self.author


class Created(models.Model):
    created = AutoCreatedField()

    class Meta:
        abstract = True

    def seconds_since_creation(self):
        delta = timezone.now() - self.created
        return delta.total_seconds()

    def is_older_than(self, seconds):
        return self.seconds_since_creation() > seconds


class Erased(models.Model):
    """Filter for valid content.
    False when something has been erased.
    """
    is_erased = models.BooleanField(
        editable=False,
        default=False,
    )

    class Meta:
        abstract = True

    def erase(self):
        self.is_erased = True
        self.save()


class Rejected(models.Model):
    """Filter for allowed content.
    False when something has been rejected/banned.
    """
    is_rejected = models.BooleanField(
        editable=False,
        default=False,
    )

    class Meta:
        abstract = True

    def allow(self):
        self.is_rejected = False
        self.save()

    def reject(self):
        self.is_rejected = True
        self.save()


class Private(models.Model):
    """Filter for public content.
    False when something is NSFW.
    """
    is_private = models.BooleanField(
        editable=False,
        default=False,
    )

    class Meta:
        abstract = True

    def show(self):
        self.is_private = False
        self.save()

    def hide(self):
        self.is_private = True
        self.save()

