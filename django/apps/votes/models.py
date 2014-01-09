from django.db import models
from django.db.models import Sum, Avg, Count

from misc import scores
from misc.models import Private, Rejected

"""This contains common code for the voting functionality.
It avoids the use of Django generic relationships and ignores most of
Django's good practices to obtain the desired database representation.
TODO:
temporary solution until I find out a cleaner way to do the same thing.
"""


class Vote(Rejected, Private):
    """Represents a vote. Any non abstract subclass must declare:
    `item`: a ForeignKey to the model that is voted.
    """
    user = models.ForeignKey(
        editable=False,
        to='users.User',
        )
    value = models.FloatField(
        editable=False,
        default=0,
        )

    class Meta:
        abstract = True

    def save(self, **kwargs):
        if self.id is None:
            self.is_private = not scores.should_it_be_public(self)
            self.is_rejected = self.user.is_rejected
        super(Vote, self).save(**kwargs)

    def get_description(self):
        if self.value > 0:
            return 'positive'
        elif self.value < 0:
            return 'negative'
        else:
            return 'neutral'


class ZVote(Vote):
    """`is_subscriber` user is subscribed to the item's zone."""
    is_subscriber = models.BooleanField(
        default=False,
        )

    def save(self, **kwargs):
        """Just sets the attributes specific to ZVote."""
        if self.id is None:
            self.is_subscriber = self.item.zone.is_subscriber(self.user)
        return super(ZVote, self).save(**kwargs)

    class Meta:
        abstract = True


class Voted(models.Model):
    """Implements vote functionality. Any concrete subclass must declare:
    `vote_through`: the vote model, must inherit from Vote.
    `voter_set`: a ManyToManyField to User, with through=vote_through.
    """
    value_function = scores.value
    value = models.FloatField(
        default=0,
        editable=False,
        )

    class Meta:
        abstract = True

    @property
    def display_value(self):
        return round(self.value * 5)

    def set_vote(self, user, value):
        model = self.vote_through
        vote, created = model.objects.get_or_create(item=self, user=user)
        if vote.value > 0 and value > 0 or vote.value < 0 and value < 1:
            vote.value = 0
        else:
            vote.value = value - user.vote_ewma / 2.0
        vote.save()
        if created:
            scores.user_vote_ewma(user, value)
            user.save()
        return vote, created

    def cast_vote(self, user, way):
        vote = self.set_vote(user, 1 if way == 'up' else -1)[0]
        self.compute_scores()
        self.save()
        return vote

    def get_vote(self, user):
        query = self.vote_through.objects.filter(item=self, user=user)
        return query.get() if query.exists() else None

    def get_votes(self):
        votes = self.vote_through.objects.filter(item=self, is_private=False)
        votes = votes.select_related('user')
        return votes

    def get_vote_count(self, **kwargs):
        votes = self.vote_through.objects.filter(item=self, **kwargs)
        total = votes.aggregate(Count('value'))['value__count']
        return 0 if total is None else total

    def get_value_avg(self, **kwargs):
        votes = self.vote_through.objects.filter(item=self, **kwargs)
        total = votes.aggregate(Avg('value'))['value__avg']
        return 0 if total is None else total

    def get_value_sum(self, **kwargs):
        votes = self.vote_through.objects.filter(item=self, **kwargs)
        total = votes.aggregate(Sum('value'))['value__sum']
        return 0 if total is None else total

    def compute_scores(self):
        self.value = self.value_function()

    def erase_scores(self):
        self.value = 0


class ZVoted(Voted):
    value_function = scores.zone_value

    class Meta:
        abstract = True

    def set_vote(self, user, value):
        vote, created = super(ZVoted, self).set_vote(user, value)
        if created:
            scores.zone_vote_ewma(self.zone, value)
            self.zone.save()
        return vote, created

