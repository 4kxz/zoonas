from captcha.fields import ReCaptchaField
from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from misc.forms import SimpleModelForm
from misc.utils import clean_slug
from .models import Submission


class SubmissionCreateForm(SimpleModelForm):
    captcha = ReCaptchaField(attrs={'theme' : 'clean'})

    class Meta:
        model = Submission
        fields = ('zone', 'title', 'link')

    def __init__(self, user=None, **kwargs):
        caption = _("Submit")
        super(SubmissionCreateForm, self).__init__(caption, **kwargs)
        self.helper.form_action = reverse('submissions:create')
        if user is not None:
            self.fields['zone'].queryset = user.subscribed_zone_set.all()

    def clean_title(self):
        title = self.cleaned_data.get('title')
        aux, slug = clean_slug(title)
        if slug == 'new':
            raise forms.ValidationError(_("Invalid title."))
        if Submission.objects.filter(slug__iexact=slug).exists():
            raise forms.ValidationError(_("Title conflict."))
        return title


class ZoneSubmissionCreateForm(SubmissionCreateForm):

    def __init__(self, **kwargs):
        super(ZoneSubmissionCreateForm, self).__init__(**kwargs)
        self.fields['zone'].widget = forms.HiddenInput()


class SubmissionUpdateForm(SimpleModelForm):

    class Meta:
        model = Submission
        fields = ('title',)

    def __init__(self, **kwargs):
        caption = _("Update")
        super(SubmissionUpdateForm, self).__init__(caption, **kwargs)


class SubmissionEraseForm(SimpleModelForm):

    class Meta:
        model = Submission
        fields = ()

    def __init__(self, **kwargs):
        caption = _("Sure, hasta la vista")
        super(SubmissionEraseForm, self).__init__(caption, **kwargs)
