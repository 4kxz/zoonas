import factory

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from users.tests import UserFactory, do_login
from zones.tests import ZoneFactory
from .models import Submission


class SubmissionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Submission
    title = factory.Sequence(lambda n: 'Submission Number {}'.format(n))
    link = "zoonas.com"
    zone = factory.SubFactory(ZoneFactory)
    author = factory.SubFactory(UserFactory)


class SimpleTest(TestCase):

    def setUp(self):
        self.client = Client()

    # Models

    def test_submission_domain(self):
        """Check submissions from the same site have the same domain.
        """
        a = SubmissionFactory(link="http://www.az.org/index.html")
        b = SubmissionFactory(link="http://www.az.org:80/about/")
        self.assertEqual(a.domain, b.domain)

    def test_submission_erase(self):
        """Check that erasing a submission removes the title and
        sets scores to 0.
        """
        submission = SubmissionFactory()
        previous_title = submission.title
        submission.erase()
        self.assertTrue(submission.is_erased)
        self.assertEqual(submission.value, 0)
        self.assertNotEqual(submission.title, previous_title)

    def test_submission_allowed_user(self):
        """Checks that normal users' content is allowed."""
        user = UserFactory()
        submission = SubmissionFactory(author=user)
        submission.save()
        self.assertFalse(submission.is_erased)
        self.assertFalse(submission.is_rejected)

    def test_submission_banned_user(self):
        """Check that banned users' content is marked as not allowed."""
        user = UserFactory()
        user.ban()
        submission = SubmissionFactory(author=user)
        self.assertFalse(submission.is_erased)
        self.assertTrue(submission.is_rejected)

    # Views

    def test_submission_page(self):
        """Check that the submission main page actually displays*
        the submission. * at least the title of.
        """
        submission = SubmissionFactory()
        response = self.client.get(submission.get_absolute_url())
        self.assertContains(response, submission.title, status_code=200)

    def test_submission_index(self):
        """Default submissions show up in the front page."""
        submission = SubmissionFactory()
        response = self.client.get(reverse('submissions:global'))
        self.assertContains(response, submission.title, status_code=200)

    def test_submission_index_erased(self):
        """Broken submissions don't show up in the front page."""
        submission = SubmissionFactory()
        submission.erase()
        response = self.client.get(reverse('submissions:global'))
        self.assertNotContains(response, submission.title, status_code=200)

    def test_submission_index_rejected(self):
        """Rejected submissions don't show up in the front page."""
        submission = SubmissionFactory()
        submission.reject()
        response = self.client.get(reverse('submissions:global'))
        self.assertNotContains(response, submission.title, status_code=200)

    def test_submission_index_private(self):
        """Private submissions don't show up in the front page."""
        submission = SubmissionFactory()
        submission.hide()
        response = self.client.get(reverse('submissions:global'))
        self.assertNotContains(response, submission.title, status_code=200)

    def test_submission_index_private_default(self):
        """Private submissions don't show up in the front page for
        default users.
        """
        do_login(self.client, UserFactory())
        submission = SubmissionFactory()
        submission.hide()
        response = self.client.get(reverse('submissions:global'))
        self.assertNotContains(response, submission.title, status_code=200)

    def test_submission_index_private_perv(self):
        """Private submissions don't show up in the front page for
        perv users.
        """
        user = UserFactory()
        user.set_perv(True)
        do_login(self.client, user)
        submission = SubmissionFactory()
        submission.hide()
        response = self.client.get(reverse('submissions:global'))
        self.assertContains(response, submission.title, status_code=200)

    def test_submission_zone(self):
        """Default submissions show up in the zone page."""
        submission = SubmissionFactory()
        response = self.client.get(submission.zone.get_absolute_url())
        self.assertContains(response, submission.title, status_code=200)

    def test_submission_zone_erased(self):
        """Broken submissions don't show up in the zone page."""
        submission = SubmissionFactory()
        submission.erase()
        response = self.client.get(submission.zone.get_absolute_url())
        self.assertNotContains(response, submission.title, status_code=200)

    def test_submission_zone_rejected(self):
        """Rejected submissions don't show up in the zone page."""
        submission = SubmissionFactory()
        submission.reject()
        response = self.client.get(submission.zone.get_absolute_url())
        self.assertNotContains(response, submission.title, status_code=200)

    def test_submission_zone_private_default(self):
        """Private submissions don't show up in the zone page for
        default users.
        """
        do_login(self.client, UserFactory())
        submission = SubmissionFactory()
        submission.hide()
        response = self.client.get(submission.zone.get_absolute_url())
        self.assertNotContains(response, submission.title, status_code=200)

    def test_submission_zone_private_perv(self):
        """Private submissions don't show up in the zone page for
        perv users.
        """
        user = UserFactory()
        user.set_perv(True)
        do_login(self.client, user)
        submission = SubmissionFactory()
        submission.hide()
        response = self.client.get(submission.zone.get_absolute_url())
        self.assertContains(response, submission.title, status_code=200)

    def test_submission_submitted(self):
        """Default submissions show up in the submitted page."""
        submission = SubmissionFactory()
        response = self.client.get(submission.author.get_submitted_url())
        self.assertContains(response, submission.title, status_code=200)

    def test_submission_submitted_erased(self):
        """Broken submissions don't show up in the submitted page."""
        submission = SubmissionFactory()
        submission.erase()
        response = self.client.get(submission.author.get_submitted_url())
        self.assertNotContains(response, submission.title, status_code=200)

    def test_submission_submitted_rejected(self):
        """Rejected submissions don't show up in the submitted page."""
        submission = SubmissionFactory()
        submission.reject()
        response = self.client.get(submission.author.get_submitted_url())
        self.assertContains(response, submission.title, status_code=200)

    def test_submission_submitted_private_default(self):
        """Private submissions don't show up in the submitted page
        by default.
        """
        do_login(self.client, UserFactory())
        submission = SubmissionFactory()
        submission.hide()
        response = self.client.get(submission.author.get_submitted_url())
        self.assertNotContains(response, submission.title, status_code=200)

    def test_submission_submitted_private_perv(self):
        """Private submissions don't show up in the submitted page for
        pervs.
        """
        user = UserFactory()
        user.set_perv(True)
        do_login(self.client, user)
        submission = SubmissionFactory()
        submission.hide()
        response = self.client.get(submission.author.get_submitted_url())
        self.assertContains(response, submission.title, status_code=200)

    def test_submission_subscribed(self):
        """Default submissions show up in the subscribed page."""
        submission = SubmissionFactory()
        submission.zone.subscribe(submission.author)
        response = self.client.get(submission.author.get_subscribed_url())
        self.assertContains(response, submission.title, status_code=200)

    def test_submission_subscribed_erased(self):
        """Broken submissions don't show up in the subscribed page."""
        submission = SubmissionFactory()
        submission.erase()
        submission.zone.subscribe(submission.author)
        response = self.client.get(submission.author.get_subscribed_url())
        self.assertNotContains(response, submission.title, status_code=200)

    def test_submission_subscribed_rejected(self):
        """Rejected submissions don't show up in the subscribed page."""
        submission = SubmissionFactory()
        submission.reject()
        submission.zone.subscribe(submission.author)
        response = self.client.get(submission.author.get_subscribed_url())
        self.assertNotContains(response, submission.title, status_code=200)

    def test_submission_subscribed_private_default(self):
        """Private submissions don't show up in the subscribed page
        by default.
        """
        do_login(self.client, UserFactory())
        submission = SubmissionFactory()
        submission.hide()
        submission.zone.subscribe(submission.author)
        response = self.client.get(submission.author.get_subscribed_url())
        self.assertNotContains(response, submission.title, status_code=200)

    def test_submission_subscribed_private_perv(self):
        """Private submissions show up in the subscribed page for pervs.
        """
        user = UserFactory()
        user.set_perv(True)
        do_login(self.client, user)
        submission = SubmissionFactory()
        submission.hide()
        submission.zone.subscribe(submission.author)
        response = self.client.get(submission.author.get_subscribed_url())
        self.assertContains(response, submission.title, status_code=200)

    # POST

    def test_login_and_submit(self):
        """Check that the general submission page (submit to any zone)
        works.
        """
        do_login(self.client, UserFactory())
        data = {'title': "Test Submission", 'link': "zoonas.com"}
        url = reverse('submissions:create')
        response = self.client.post(url, data, follow=True)
        self.assertContains(response, data['title'], status_code=200)

    def test_login_and_vote_positive(self):
        """Check that the vote view submits the vote.
        """
        submission = SubmissionFactory()
        initial_count = submission.submissionvote_set.count()
        do_login(self.client, UserFactory())
        data = {'vote': 'up'}
        url = submission.get_vote_url()
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        submission = Submission.objects.get(pk=submission.pk)  # Update
        final_count = submission.submissionvote_set.count()
        self.assertEqual(final_count, initial_count + 1)

    # Access

    def test_create_login(self):
        response = self.client.get(reverse('submissions:create'))
        self.assertEqual(response.status_code, 302)

    def test_create_user_ok(self):
        do_login(self.client, UserFactory())
        response = self.client.get(reverse('submissions:create'))
        self.assertEqual(response.status_code, 200)

    def test_global_ok(self):
        resp = self.client.get(reverse('submissions:global'))
        self.assertEqual(resp.status_code, 200)

    def test_global_recent_ok(self):
        resp = self.client.get(reverse('submissions:global')+'?sort=recent')
        self.assertEqual(resp.status_code, 200)

    def test_global_best_ok(self):
        resp = self.client.get(reverse('submissions:global')+'?sort=best')
        self.assertEqual(resp.status_code, 200)


#     def test_submit_user_200_missing_data(self):
#         response = self.c.post(reverse('account:login'), user_data)
#         response = self.c.post(reverse('submissions:create'), sub_data_missing)
#         self.assertEqual(response.status_code, 200)
#         # TODO: Check form ID
