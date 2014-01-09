import random
import string

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _

from misc.models import Rejected, Erased
from misc.fields import AutoCreatedField


class UserManager(BaseUserManager):

    def create_user(self, username, password=None):
        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(username, password)
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def random_username(self):
        l = settings.USER_NAME_LENGTH
        generate = lambda : ''.join(random.sample(string.ascii_lowercase, l))
        r = generate()
        while self.filter(username=r).exists():
            r = generate()
        return r

    def get_default(self):
        return self.get(pk=1)


class User(AbstractBaseUser, Rejected, Erased):
    USERNAME_FIELD = 'username'
    username = models.CharField(
        unique=True,
        max_length=settings.USER_NAME_LENGTH,
        db_index=True,
        )
    is_active = models.BooleanField(
        editable=False,
        default=True,
        )
    is_superuser = models.BooleanField(
        editable=False,
        default=False,
        )
    is_perv = models.BooleanField(
        editable=False,
        default=False,
        )
    vote_ewma = models.FloatField(
        editable=False,
        default=0,
        )
    join_date = AutoCreatedField()
    objects = UserManager()

    class Meta:
        ordering = ['username']

    def set_perv(self, is_perv):
        self.is_perv = is_perv
        self.save()

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def get_public_name(self):
        return _("Erased user") if self.is_erased else self.username

    def get_moderated_zones(self):
        return self.moderated_zone_set.all()

    def subscription_count(self):
        return self.subscription_set.count()

    def erase(self):
        self.username = User.objects.random_username()
        self.subscribed_zone_set.clear()
        self.moderated_zone_set.clear()
        self.is_active = False
        super(User, self).erase()

    def ban(self):
        self.moderated_zone_set.clear()
        self.is_active = False
        super(User, self).reject()

    def __unicode__(self):
        return self.username

    def get_absolute_url(self):
        return self.get_about_url()

    def get_about_url(self):
        return reverse('profiles:about', args=[self.username])

    def get_evaluate_url(self):
        return reverse('profiles:evaluate', args=[self.username])

    def get_report_url(self):
        return reverse('profiles:report', args=[self.username])

    def get_submitted_url(self):
        return reverse('profiles:submitted', args=[self.username])

    def get_subscribed_url(self):
        return reverse('profiles:subscribed', args=[self.username])
