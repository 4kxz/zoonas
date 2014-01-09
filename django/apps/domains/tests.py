from django.test import TestCase

from .models import DomainName


class SimpleTest(TestCase):

    def test_simple_domain_unicode(self):
        url = "example.com"
        dn = DomainName.objects.obtain(url)
        self.assertEqual(unicode(dn), "example.com")

    def test_subdomain_unicode(self):
        url = "http://some.example.org/?whatever=12"
        dn = DomainName.objects.obtain(url)
        self.assertEqual(unicode(dn), "some.example.org")
        self.assertEqual(unicode(dn.subdomain), "some")
        self.assertEqual(unicode(dn.domain), "example.org")

    def test_another_domain_unicode(self):
        url = "http://some.other.example.co.uk/something/else/"
        dn = DomainName.objects.obtain(url)
        self.assertEqual(unicode(dn), "some.other.example.co.uk")
        self.assertEqual(unicode(dn.subdomain), "some.other")
        self.assertEqual(unicode(dn.domain), "example.co.uk")

    def test_subdomain_reject(self):
        url = "http://some.other.example-a.co.uk/something/else/"
        dn = DomainName.objects.obtain(url)
        dn.reject()
        self.assertFalse(dn.domain.is_rejected)
        self.assertTrue(dn.is_rejected)

    def test_domain_reject(self):
        url = "http://some.other.example-b.co.uk/something/else/"
        dn = DomainName.objects.obtain(url)
        dn.domain.reject()
        url = "http://some.other.example-b.co.uk/something/else/"
        dn = DomainName.objects.obtain(url)
        self.assertTrue(dn.domain.is_rejected)
        self.assertTrue(dn.is_rejected)

    def test_sibling_reject(self):
        url = "http://some.example-c.co.uk/something/"
        dna = DomainName.objects.obtain(url)
        url = "http://some.other.example-c.co.uk/something/"
        dnb = DomainName.objects.obtain(url)
        dna.domain.reject()
        url = "http://some.example-c.co.uk/something/"
        dna = DomainName.objects.obtain(url)
        url = "http://some.other.example-c.co.uk/something/"
        dnb = DomainName.objects.obtain(url)
        self.assertTrue(dna.is_rejected)
        self.assertTrue(dnb.is_rejected)
        self.assertTrue(dna.domain.is_rejected)
