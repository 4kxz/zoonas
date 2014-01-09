import factory
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.utils.translation import ugettext as _

from .models import User


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: 'UserNumber{}'.format(n))


class AdminFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: 'AdminNumber{}'.format(n))
    is_superuser = True


class UserTest(TestCase):

    def setUp(self):
        self.client = Client()

    # Models

    def test_erase(self):
        """Check that the erased user is disabled and its
        username removed.
        """
        user = UserFactory()
        previous_username = user.username
        user.erase()
        self.assertTrue(user.is_erased)
        self.assertFalse(user.is_active)
        self.assertNotEqual(user.username, previous_username)
        self.assertEqual(user.get_public_name(), _("Erased user"))

    def test_ban(self):
        """Check that the banned user can't log in."""
        user = UserFactory()
        previous_username = user.username
        user.ban()
        self.assertFalse(user.is_erased)
        self.assertTrue(user.is_rejected)
        self.assertFalse(user.is_active)
        self.assertEqual(user.username, previous_username)
        self.assertEqual(user.get_public_name(), previous_username)

    def test_reject(self):
        """Check that the rejected user can log in but is shadowbanned.
        """
        user = UserFactory()
        previous_username = user.username
        user.reject()
        self.assertFalse(user.is_erased)
        self.assertTrue(user.is_rejected)
        self.assertTrue(user.is_active)
        self.assertEqual(user.username, previous_username)
        self.assertEqual(user.get_public_name(), previous_username)

    # Views access

    def test_main_ok(self):
        response = self.client.get(UserFactory().get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_about_ok(self):
        response = self.client.get(UserFactory().get_about_url())
        self.assertEqual(response.status_code, 200)

    def test_submitted_ok(self):
        response = self.client.get(UserFactory().get_submitted_url())
        self.assertEqual(response.status_code, 200)

    def test_subscribed_ok(self):
        response = self.client.get(UserFactory().get_subscribed_url())
        self.assertEqual(response.status_code, 200)

    # Views

    def test_account_login(self):
        user = UserFactory()
        response = self.client.get(reverse('frontpage'))
        self.assertNotContains(response, user.username, status_code=200)
        do_login(self.client, user)
        response = self.client.get(reverse('frontpage'))
        self.assertContains(response, user.username, status_code=200)

    def test_account_logout_get(self):
        do_login(self.client, UserFactory())
        response = self.client.get(reverse('account:logout'))
        self.assertTrue(response.context['user'].is_authenticated())

    def test_account_logout_post(self):
        do_login(self.client, UserFactory())
        response = self.client.post(reverse('account:logout'), {}, follow=True)
        self.assertFalse(response.context['user'].is_authenticated())

    def test_account_password_change(self):
        p_old = 'OldPassword'
        p_new = 'NewPassword'
        do_login(self.client, UserFactory(), password=p_old)
        url = reverse('account:password')
        data = {
            'password': p_old,
            'new_password_1': p_new,
            'new_password_2': p_new,
            }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].check_password(p_old))
        self.assertTrue(response.context['user'].check_password(p_new))

    def test_account_erase(self):
        user = UserFactory()
        password = "ErasePassword"
        do_login(self.client, user, password=password)
        url = reverse('account:erase')
        data = {
            'username': user.username,
            'password': password,
            }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_active)


def do_login(client, user, password="PASSWORD"):
    user.set_password(password)
    user.save()
    return client.login(username=user.username, password=password)
