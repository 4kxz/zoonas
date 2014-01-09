from crispy_forms.layout import Hidden
from django import forms
from django.utils.translation import ugettext_lazy as _

from misc.forms import SimpleForm, SimpleModelForm
from misc.utils import clean_slug
from .models import Proposal, Zone


class ZoneCreateForm(SimpleModelForm):

    class Meta:
        model = Zone
        fields = ('name', 'description', )
        widgets = {'description': forms.widgets.Textarea(attrs={'rows': 2})}

    def __init__(self, **kwargs):
        caption = _("Create")
        super(ZoneCreateForm, self).__init__(caption, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        aux, slug = clean_slug(name)
        if slug == 'new':
            raise forms.ValidationError(_("Invalid name."))
        if Zone.objects.filter(slug__iexact=slug).exists():
            raise forms.ValidationError(_("Name conflict with existing zone."))
        return name


class ZoneUpdateForm(SimpleModelForm):

    class Meta:
        model = Zone
        fields = ('description', 'information', )
        widgets = {
            'description': forms.widgets.Textarea(attrs={'rows': 2}),
            'information': forms.widgets.Textarea(attrs={'rows': 8}),
            }

    def __init__(self, **kwargs):
        caption = _("Update")
        super(ZoneUpdateForm, self).__init__(caption, **kwargs)


class SubscriptionForm(SimpleForm):

    def __init__(self, zone, add, **kwargs):
        if add:
            do, caption = 'add', _("Join {}")
        else:
            do, caption = 'remove', _("Leave {}")
        caption = caption.format(zone.name)
        action = zone.get_subscription_url()
        super(SubscriptionForm, self).__init__(caption, action, **kwargs)
        self.helper.add_input(Hidden('subscription', do))
        self.helper.form_class = ' '.join(('subscription', do))


class GrantPermissionForm(SimpleForm):

    username = forms.CharField(label=_('Username'))

    def __init__(self, zone, **kwargs):
        caption =  _("Add")
        action = zone.get_permissions_url()
        super(GrantPermissionForm, self).__init__(caption, action, **kwargs)
        self.helper.add_input(Hidden('permission', 'grant'))
        self.helper.form_class = ' '.join(('permission', 'grant'))


class RevokePermissionForm(SimpleForm):

    def __init__(self, zone, user, **kwargs):
        caption = _("Remove")
        action = zone.get_permissions_url()
        super(RevokePermissionForm, self).__init__(caption, action, **kwargs)
        self.helper.add_input(Hidden('username', user.username))
        self.helper.add_input(Hidden('permission', 'revoke'))
        self.helper.form_class = ' '.join(('permission', 'revoke'))


class ProposalCreateForm(SimpleModelForm):

    class Meta:
        model = Proposal
        fields = ('name', 'description', )
        widgets = {'description': forms.widgets.Textarea(attrs={'rows': 2})}

    def __init__(self, **kwargs):
        caption = _("Create")
        super(ProposalCreateForm, self).__init__(caption, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        aux, slug = clean_slug(name)
        if slug == 'new':
            raise forms.ValidationError(_("Invalid name."))
        exists = lambda model: model.objects.filter(slug__iexact=slug).exists()
        if exists(Proposal) or exists(Zone):
            raise forms.ValidationError(_("Name conflict with existing zone."))
        return name
