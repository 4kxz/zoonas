import factory
import random
import string

from django.test import TestCase
from django.test.client import Client

from users.tests import UserFactory, do_login
from .models import Note


def random_text(n):
    return ''.join(random.choice(string.lowercase) for i in range(25))


class NoteFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Note
    author = factory.SubFactory(UserFactory)
    text = factory.Sequence(random_text)


class NoteTest(TestCase):

    def setUp(self):
        self.client = Client()

    # Models

    # Views

    def test_note_page(self):
        """Check that the note main page actually displays the note."""
        note = NoteFactory()
        do_login(self.client, UserFactory())
        response = self.client.get(note.get_absolute_url())
        self.assertContains(response, note.text, status_code=200)
        self.assertContains(response, note.author.username, status_code=200)
