import math

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from misc.models import Author, Created, Private
from misc.utils import clean_slug
from votes.models import Vote, Voted, ZVote, ZVoted
from users.models import User


class ZoneManager(models.Manager):

    def get_default(self):
        return self.get(pk=1)


class ZoneVote(ZVote):
    """Concrete Vote class."""
    item = models.ForeignKey(
        to='zones.Zone',
        )
    unique_together = (('item', 'user'),)


class Zone(Created, Private, ZVoted):
    slug = models.SlugField(
        editable=False,
        unique=True,
        db_index=True,
        max_length=settings.ZONE_NAME_LENGTH,
        )
    name = models.CharField(
        max_length=settings.ZONE_NAME_LENGTH,
        verbose_name=_('name'),
        )
    description = models.CharField(
        blank=True,
        max_length=settings.ZONE_DESCRIPTION_LENGTH,
        verbose_name=_('short description'),
        )
    information = models.CharField(
        blank=True,
        max_length=settings.ZONE_INFORMATION_LENGTH,
        verbose_name=_('information for users'),
        )
    thumbnail = models.ImageField(
        editable=False,
        upload_to='thumbnails/submissions',
        )
    size = models.SmallIntegerField(
        editable=False,
        default=0,
        )
    vote_ewma = models.FloatField(
        editable=False,
        default=0,
        )
    score_ewma = models.FloatField(
        editable=False,
        default=0,
        )
    objects = ZoneManager()

    class Meta:
        ordering = ['-value', '-size']

    @property
    def zone(self):
        return self

    def save(self, **kwargs):
        if self.id is None:
            self.name, self.slug = clean_slug(self.name)
        super(Zone, self).save(**kwargs)

    # Subscriptions
    subscriber_set = models.ManyToManyField(
        editable=False,
        to='users.User',
        through='Subscription',
        related_name='subscribed_zone_set',
        )

    def is_subscriber(self, user):
        if not user.is_authenticated():
            return False
        return self.subscription_set.filter(user=user).exists()

    def subscribe(self, user):
        Subscription.objects.get_or_create(zone=self, user=user)
        self.size = self.subscriber_set.count()
        self.save()

    def unsubscribe(self, user):
        self.subscription_set.filter(user=user).delete()
        self.size = self.subscriber_set.count()
        self.save()

    # Permissions
    moderator_set = models.ManyToManyField(
        editable=False,
        to='users.User',
        through='Permission',
        related_name='moderated_zone_set',
        )

    def is_moderator(self, user):
        is_user = user.is_authenticated()
        return is_user and self.permission_set.filter(user=user).exists()

    def is_admin(self, user):
        try:
            is_user = user.is_authenticated()
            return is_user and self.permission_set.get(user=user).is_admin
        except Zone.DoesNotExist:
            return False

    def is_superior(self, strong, weak):
        if strong == weak:
            return True
        if not self.is_moderator(strong):
            return False
        if not self.is_moderator(weak):
            return True
        strong_perm = self.permission_set.get(user=strong)
        weak_perm = self.permission_set.get(user=weak)
        return strong_perm > weak_perm

    def add_founder(self, target):
        Permission.objects.get_or_create(zone=self, user=target)
        self.subscribe(target)

    def grant_permission(self, target, moderator):
        if not moderator.is_superuser and not self.is_moderator(moderator):
            raise ValueError("Granting permissions requires a moderator")
        if self.moderator_count() >= settings.MODERATOR_LIMIT:
            raise ValueError("Limit of moderators exceeded")
        if target.is_rejected:
            raise ValueError("Banned users are not allowed to moderate")
        if target.is_erased:
            raise ValueError("Erased users are not allowed to moderate")
        if Permission.objects.filter(zone=self, user=target).exists():
            raise ValueError("User is already a moderator")
        Permission.objects.create(zone=self, user=target)

    def revoke_permission(self, target, moderator):
        super_mod = moderator.is_superuser
        if not super_mod and not self.is_moderator(moderator):
            raise ValueError("Revoking permissions requires a moderator")
        if not super_mod and not self.is_superior(moderator, target):
            raise ValueError("Removing superiors is forbidden")
        if not Permission.objects.filter(zone=self, user=target).exists():
            raise ValueError("User is not a moderator")
        self.permission_set.filter(user=target).delete()

    def permissions(self):
        return self.permission_set.all()

    def moderators(self):
        return self.moderator_set.all()

    def moderator_count(self):
        return self.moderator_set.count()

    # Votes
    vote_through = ZoneVote
    voter_set = models.ManyToManyField(
        editable=False,
        to='users.User',
        through=vote_through,
        related_name='voted_zone_set',
        )

    # Other stuff

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('zones:main', args=[self.slug])

    def get_about_url(self):
        return reverse('zones:about', args=[self.slug])

    def get_reported_url(self):
        return reverse('zones:reported', args=[self.slug])

    def get_rejected_url(self):
        return reverse('zones:rejected', args=[self.slug])

    def get_submit_url(self):
        return reverse('zones:submit', args=[self.slug])

    def get_subscription_url(self):
        return reverse('zones:subscriptions', args=[self.slug])

    def get_settings_url(self):
        return reverse('zones:settings', args=[self.slug])

    def get_permissions_url(self):
        return reverse('zones:permissions', args=[self.slug])


class Subscription(models.Model):
    zone = models.ForeignKey(
        to=Zone,
        )
    user = models.ForeignKey(
        to='users.User',
        )
    order = models.IntegerField(
        default=0,
        )

    class Meta:
        unique_together = (('user', 'zone'),)
        ordering = ['-order']


class Permission(Created):
    zone = models.ForeignKey(
        to=Zone,
        )
    user = models.ForeignKey(
        to='users.User',
        )
    is_admin = models.BooleanField(
        default=False,
        )

    class Meta:
        unique_together = (('zone', 'user'),)
        ordering = ['created']

    def __cmp__(self, other):
        return self.created < other.created


class ProposalVote(Vote):
    item = models.ForeignKey(
        to='zones.Proposal',
        )
    unique_together = (('item', 'user'),)


class Proposal(Author, Created, Voted):
    slug = models.SlugField(
        editable=False,
        unique=True,
        db_index=True,
        max_length=settings.ZONE_NAME_LENGTH,
        )
    name = models.CharField(
        max_length=settings.ZONE_NAME_LENGTH,
        verbose_name=_('name'),
        )
    description = models.CharField(
        blank=True,
        max_length=settings.ZONE_DESCRIPTION_LENGTH,
        verbose_name=_('short description'),
        )
    vote_through = ProposalVote
    voter_set = models.ManyToManyField(
        editable=False,
        to='users.User',
        through=vote_through,
        related_name='voted_zone_proposal_set',
        )

    class Meta:
        ordering = ['-value']

    def save(self, **kwargs):
        if self.id is None:
            self.name, self.slug = clean_slug(self.name)
            super(Proposal, self).save(**kwargs)
            self.cast_vote(user=self.author, value='up')
        else:
            super(Proposal, self).save(**kwargs)

    def cast_vote(self, user, value):
        vote  = super(Proposal, self).cast_vote(user, value)
        # Decide wether to create or not the zone.
        if self.score >= self.threshold:
            zone = Zone()
            zone.name = self.name
            zone.description = self.description
            zone.save()
            zone.add_founder(self.author)
            self.delete()
        return vote

    @property
    def threshold(self):
        return 5 * math.log(User.objects.count())

    @property
    def score(self):
        score = self.proposalvote_set.filter(value__gt=0).count()
        bonus = (self.get_value_avg() + 1) / 4 * self.threshold
        return score + bonus

    @property
    def progress(self):
        return "{:0.0f}%".format(100 * self.score / self.threshold)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('zones:proposals_index')

    def get_vote_url(self):
        return reverse('zones:proposals_vote', args=[self.slug])
