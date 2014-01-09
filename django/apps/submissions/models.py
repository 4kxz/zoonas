from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from domains.models import DomainName
from comments.models import Commented
from misc import scores
from misc.models import Author, Created, Erased, Private, Rejected
from misc.utils import clean_slug
from users.models import User
from votes.models import ZVote, ZVoted
from zones.models import Zone
from .tasks import thumbnail_task


class SubmissionManager(models.Manager):
    """Manager with additional filtering options."""
    ORDERING = {
        'recent': ('-created', '-value'),
        'best': ('-value', '-created'),
        'global': ('-global_score', '-created'),
        'zone': ('-zone_score', '-created'),
        }

    def custom(self, user=None, order=None, **kwargs):
        """Filters the queryset, custom arguments:
        `user` is passed to filter submissions according to user settings.
        `order` sorts submissions according to `SubmissionManager.ORDERING`.
        """
        if user is None:
            user = User.objects.get_default()
        # Add some defaults.
        if not user.is_superuser:
            kwargs.setdefault('is_erased', False)
        if not user.is_authenticated() or not user.is_perv:
            kwargs.setdefault('is_private', False)
        # Filter proper.
        submissions = super(SubmissionManager, self).filter(**kwargs)
        # Orders are presets from ORDERING, default sort is defined in model.
        order_by = SubmissionManager.ORDERING.get(order)
        if order_by is not None:
            submissions = submissions.order_by(*order_by)
        return submissions

    def from_subscriptions(self, subscriber, **kwargs):
        """Returns submissions from zones in the subscriber's subscriptions."""
        # FIXME: There must be a way to avoid looping.
        subscribed_zones = subscriber.subscribed_zone_set.all()
        if subscribed_zones:
            query = models.Q()
            for zone in subscribed_zones:
                query = query | models.Q(zone=zone)
            return self.custom(**kwargs).filter(query)
        else:
            return self.none()


class SubmissionVote(ZVote):
    """Concrete Vote class."""
    item = models.ForeignKey(
        to='submissions.Submission',
        )
    unique_together = (('item', 'user'),)


class Submission(Author, Created, Erased, Rejected, Private, ZVoted, Commented):
    """Submissions have a title and a link/text.
    The rest is stuff to filter, sort or display them.
    """
    slug = models.SlugField(
        editable=False,
        unique=True,
        db_index=True,
        max_length=settings.SUBMISSION_SLUG_LENGTH,
        )
    title = models.CharField(
        verbose_name=_('title'),
        max_length=settings.SUBMISSION_TITLE_LENGTH,
        )
    link = models.URLField(
        verbose_name=_('link'),
        )
    domain = models.ForeignKey(
        editable=False,
        to='domains.DomainName',
        )
    thumbnail = models.ImageField(
        editable=False,
        upload_to='thumbnails/submissions',
        )
    zone = models.ForeignKey(
        verbose_name=_('zone'),
        to='zones.Zone',
        )
    objects = SubmissionManager()

    def save(self, **kwargs):
        if self.id is None:
            self.domain = DomainName.objects.obtain(self.link)
            self.title, self.slug = clean_slug(self.title)
            self.is_rejected = self.author.is_rejected or self.domain.is_rejected
            super(Submission, self).save(**kwargs)
            self.base_score = scores.base_score(self, Zone.objects.get_default())
            self.cast_vote(user=self.author, way='up')
            if (not self.is_rejected):
                # Update exponential moving average score for current zone.
                scores.zone_score_ewma(self.zone, self.base_score)
                self.zone.save()
                # Gnerate thumbnail.
                thumbnail_task.delay(Submission, self.pk)
        else:
            super(Submission, self).save(**kwargs)

    def erase(self):
        self.author = User.objects.get_default()
        self.zone = Zone.objects.get_default()
        self.title = _("Erased submission")
        self.link = reverse('frontpage')
        self.erase_scores()
        super(Submission, self).erase()

    # Voted attributes
    base_score = models.FloatField(
        editable=False,
        default=0,
        )
    zone_score = models.FloatField(
        editable=False,
        default=0,
        )
    global_score = models.FloatField(
        editable=False,
        default=0,
        )
    vote_through = SubmissionVote
    voter_set = models.ManyToManyField(
        editable=False,
        to='users.User',
        through=vote_through,
        related_name='voted_submission_set',
        )

    def compute_scores(self):
        super(Submission, self).compute_scores()
        self.zone_score = scores.zone_score(self)
        self.global_score = scores.global_score(self)

    def erase_scores(self):
        super(Submission, self).erase_scores()
        self.zone_score = 0
        self.global_score = 0

    # Other stuff

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('submissions:details', args=[self.slug])

    def get_comments_url(self):
        return reverse('submissions:details', args=[self.slug]) + '#comments'

    def get_comment_url(self):
        return reverse('submissions:comment', args=[self.slug])

    def get_update_url(self):
        return reverse('submissions:update', args=[self.slug])

    def get_erase_url(self):
        return reverse('submissions:erase', args=[self.slug])

    def get_vote_url(self):
        return reverse('submissions:vote', args=[self.slug])

    def get_report_url(self):
        return reverse('submissions:report', args=[self.slug])

    def get_evaluate_url(self):
        return reverse('submissions:evaluate', args=[self.slug])

    def get_thumbnail_url(self):
        show = not self.is_erased and not self.is_rejected and self.thumbnail
        return self.thumbnail.url if show else None
