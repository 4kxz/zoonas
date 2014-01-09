from captcha.fields import ReCaptchaField
from django import forms
from django.utils.translation import ugettext as _

from misc.forms import SimpleForm, SimpleModelForm
from .models import Report


class ReportCreateForm(SimpleModelForm):
    note = forms.CharField(widget=forms.Textarea)
    captcha = ReCaptchaField(attrs={'theme' : 'clean'})

    class Meta:
        model = Report
        fields = ()

    def __init__(self, **kwargs):
        caption = _("Report")
        super(ReportCreateForm, self).__init__(caption, **kwargs)


class ReportResolveForm(SimpleForm):

    def __init__(self, report, **kwargs):
        action = report.get_resolve_url()
        caption = _("Resolve")
        super(ReportResolveForm, self).__init__(caption, action, **kwargs)

