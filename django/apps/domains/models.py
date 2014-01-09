from tldextract import extract
from django.db import models

from misc.models import Private, Rejected


class Domain(Rejected, Private):
    """A second-level domain name."""
    domain = models.CharField(
        max_length=100,
        unique=True,
        )

    class Meta:
        ordering = ['domain']

    def hide(self):
        self.domain_names.update(is_private=True)
        super(Domain, self).hide()

    def reject(self):
        self.domain_names.update(is_rejected=True)
        super(Domain, self).reject()

    def __unicode__(self):
        return unicode(self.domain)


class DomainNameManager(models.Manager):

    def obtain(self, url):
        """Returns the `DomainName` object associated with the passed
        `url`. Creating it when necessary.
        """
        ext = extract(url)  # "http://www.forums.example.co.uk"
        domain = '.'.join(ext[-2:])  # "example.co.uk"
        subdomain = ext.subdomain  # "www.forums"
        domain, created = Domain.objects.get_or_create(domain=domain)
        domain_name = self.get_or_create(domain=domain, subdomain=subdomain)[0]
        if not created:
            domain_name.is_private = domain.is_private
            domain_name.is_rejected = domain.is_rejected
            domain_name.save()
        return domain_name


class DomainName(Rejected, Private):
    """A domain + subdomain name."""
    domain = models.ForeignKey(
        Domain,
        related_name='domain_names',
        )
    subdomain = models.CharField(
        max_length=100,
        )
    objects = DomainNameManager()

    class Meta:
        unique_together = ('domain', 'subdomain')
        ordering = ['domain', 'subdomain']

    def count(self):
        return self.submission_set.count()

    def __unicode__(self):
        if self.subdomain:
            name = self.subdomain, unicode(self.domain)
            return '.'.join(name)
        else:
            return unicode(self.domain)
