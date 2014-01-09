from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.core.urlresolvers import reverse
from django.db import models

from misc.models import Rejected
from votes.models import Vote, Voted


class CommentManager(models.Manager):

    def filter_item(self, item):
        content_type = ContentType.objects.get_for_model(item)
        return self.filter(item_content_type=content_type, item_id=item.id)


class CommentVote(Vote):
    item = models.ForeignKey(
        editable=False,
        to='comments.Comment',
        )
    unique_together = (('item', 'user'),)


class Comment(Voted, Rejected):
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
    parent = models.ForeignKey(
        editable=False,
        to='comments.Comment',
        null=True,
        )
    objects = CommentManager()

    # Voted attributes
    vote_through = CommentVote
    voter_set = models.ManyToManyField(
        editable=False,
        to='users.User',
        through=vote_through,
        related_name='voted_comment_set',
        )

    class Meta:
        ordering = ['note__created']

    def save(self, **kwargs):
        if self.id is None:
            try:
                self.is_rejected = self.author.is_rejected
                self.is_private = self.item.is_private
            except AttributeError:
                pass
        return super(Comment, self).save(**kwargs)

    def __unicode__(self):
        return unicode(self.note)

    def get_absolute_url(self):
        return self.item.get_absolute_url() + '#comment-{}'.format(self.pk)

    def get_evaluate_url(self):
        return reverse('comments:evaluate', args=[self.pk])

    def get_reply_url(self):
        return reverse('comments:reply', args=[self.pk])

    def get_report_url(self):
        return reverse('comments:report', args=[self.pk])

    def get_vote_url(self):
        return reverse('comments:vote', args=[self.pk])


class Commented(models.Model):
    comment_count = models.IntegerField(
        editable=False,
        default=0,
        )

    class Meta:
        abstract = True

    def get_comments(self):
        comments = Comment.objects.filter_item(item=self)
        comments = comments.select_related('note', 'note__author')
        comments = comments.prefetch_related('item')
        return comments

    def update_comment_count(self):
        self.comment_count = self.get_comments().count()
