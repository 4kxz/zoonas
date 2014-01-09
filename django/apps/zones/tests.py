import factory

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from users.tests import UserFactory, AdminFactory, do_login
from .models import Zone


class ZoneFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Zone

    name = factory.Sequence(lambda n: 'Zone Number {}'.format(n))


def get_moderator(zone):
    """Returns a fresh moderator for `zone`."""
    user = UserFactory()
    zone.add_founder(user)
    return user


class SimpleTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.zone = ZoneFactory()

    # Models

    def test_name_spaces(self):
        """Spaces are stripped from the title."""
        zone = ZoneFactory(name=u" A name with   spaces  ")
        self.assertEqual(zone.name, u"A name with spaces")

    def test_slug_spaces(self):
        """Spaces are replaced with dashes in the slug."""
        zone = ZoneFactory(name=u" A name with   spaces  ")
        self.assertEqual(zone.slug, u"a-name-with-spaces")

    def test_slug_bullshit(self):
        """Funny characters are removed from the slug."""
        zone = ZoneFactory(name=u"  $/:(.;A-//4  >")
        self.assertEqual(zone.slug, u"a-4")

    def test_not_subscriber(self):
        """New users don't have a subscription. Of course not. Stupid test.
        """
        user = UserFactory()
        self.assertFalse(self.zone.is_subscriber(user))

    def test_add_subscriber(self):
        """A user should be a subscriber after adding a subscription."""
        user = UserFactory()
        self.zone.subscribe(user)
        self.assertTrue(self.zone.is_subscriber(user))

    def test_remove_subscriber(self):
        """A user should not be a subscriber after removing a subscription.
        """
        user = UserFactory()
        self.zone.subscribe(user)
        self.assertTrue(self.zone.is_subscriber(user))
        self.zone.unsubscribe(user)
        self.assertFalse(self.zone.is_subscriber(user))

    def test_not_moderator(self):
        """A new user should not be a moderator, or else something's
        very broken.
        """
        user = UserFactory()
        self.assertFalse(self.zone.is_moderator(user))

    def test_add_moderator(self):
        """A newly added moderator should be a moderator. - Captain Obvious
        """
        mod = get_moderator(self.zone)
        user = UserFactory()
        self.zone.grant_permission(user, mod)
        self.assertTrue(self.zone.is_moderator(user))

    def test_remove_moderator(self):
        """Adding and removing a moderator could collapse the universe."""
        mod = get_moderator(self.zone)
        user = UserFactory()
        self.zone.grant_permission(user, mod)
        self.assertTrue(self.zone.is_moderator(user))
        self.zone.revoke_permission(user, mod)
        self.assertFalse(self.zone.is_moderator(user))

    def test_add_twice_then_remove_moderator(self):
        """Let's test idempotence. Just in case somene gets superpowers twice.
        """
        mod = get_moderator(self.zone)
        user = UserFactory()
        self.zone.grant_permission(user, mod)
        self.assertRaises(ValueError, self.zone.grant_permission, user, mod)
        self.zone.revoke_permission(user, mod)
        self.assertFalse(self.zone.is_moderator(user))

    def test_add_then_remove_twice_moderator(self):
        """Removing a mod twice? More on idempotence. We're really paranoid.
        """
        mod = get_moderator(self.zone)
        user = UserFactory()
        self.zone.grant_permission(user, mod)
        self.zone.revoke_permission(user, mod)
        self.assertRaises(ValueError, self.zone.revoke_permission, user, mod)
        self.assertFalse(self.zone.is_moderator(user))

    def test_add_founder(self):
        """Pioneers should be awarded the highest rank.
        I don't think this is actually used though.
        """
        user = UserFactory()
        self.zone.add_founder(user)
        self.assertTrue(self.zone.is_moderator(user))
        self.assertTrue(self.zone.is_subscriber(user))

    # Access

    def test_create_login(self):
        response = self.client.get(reverse('zones:create'))
        self.assertEqual(response.status_code, 302)

    def test_create_user_denied(self):
        do_login(self.client, UserFactory())
        response = self.client.get(reverse('zones:create'))
        self.assertEqual(response.status_code, 403)

    def test_create_admin_ok(self):
        do_login(self.client, AdminFactory())
        response = self.client.get(reverse('zones:create'))
        self.assertEqual(response.status_code, 200)

    def test_frontpage_ok(self):
        response = self.client.get(self.zone.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_frontpage_sort_recent_ok(self):
        response = self.client.get(self.zone.get_absolute_url() + '?sort=recent')
        self.assertEqual(response.status_code, 200)

    def test_frontpage_sort_best_ok(self):
        response = self.client.get(self.zone.get_absolute_url() + '?sort=best')
        self.assertEqual(response.status_code, 200)

    def test_frontpage_user_ok(self):
        do_login(self.client, UserFactory())
        response = self.client.get(self.zone.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_about_ok(self):
        response = self.client.get(self.zone.get_about_url())
        self.assertEqual(response.status_code, 200)

    def test_settings_login(self):
        response = self.client.get(self.zone.get_settings_url())
        self.assertEqual(response.status_code, 302)

    def test_settings_user_denied(self):
        do_login(self.client, UserFactory())
        response = self.client.get(self.zone.get_settings_url())
        self.assertEqual(response.status_code, 403)

    def test_settings_mod_ok(self):
        do_login(self.client, get_moderator(self.zone))
        response = self.client.get(self.zone.get_settings_url())
        self.assertEqual(response.status_code, 200)

    def test_settings_admin_ok(self):
        do_login(self.client, AdminFactory())
        response = self.client.get(self.zone.get_settings_url())
        self.assertEqual(response.status_code, 200)
