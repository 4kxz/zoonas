from django import forms
from django.utils.translation import ugettext as _

from misc.forms import SimpleModelForm
from .models import Note


class NoteEditForm(SimpleModelForm):

    class Meta:
        model = Note
        widgets = {'text': forms.widgets.Textarea()}

    def __init__(self, **kwargs):
        caption = _("Update")
        super(NoteEditForm, self).__init__(caption, **kwargs)


class NoteEraseForm(SimpleModelForm):

    class Meta:
        model = Note
        fields = ()

    def __init__(self, **kwargs):
        caption = _("Sure, hasta la vista")
        super(NoteEraseForm, self).__init__(caption, **kwargs)
