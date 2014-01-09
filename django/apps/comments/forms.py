from captcha.fields import ReCaptchaField
from django import forms
from django.utils.translation import ugettext as _

from misc.forms import SimpleModelForm
from .models import Comment


class CommentCreateForm(SimpleModelForm):
    note = forms.CharField(widget=forms.Textarea)
    captcha = ReCaptchaField(attrs={'theme': 'clean'})

    class Meta:
        model = Comment
        fields = ()

    def __init__(self, **kwargs):
        caption = _("Comment")
        super(CommentCreateForm, self).__init__(caption, **kwargs)


class CommentReplyForm(SimpleModelForm):
    note = forms.CharField(widget=forms.Textarea)
    captcha = ReCaptchaField(attrs={'theme': 'clean'})

    class Meta:
        model = Comment
        fields = ()

    def __init__(self, **kwargs):
        caption = _("Reply")
        super(CommentReplyForm, self).__init__(caption, **kwargs)
