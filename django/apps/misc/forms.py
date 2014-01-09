from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.http import urlquote


class SimpleForm(forms.Form):
    """Simple form with a helper that takes an action and a next
    parameter.
    """

    def __init__(self, caption="Submit", action="", next=None, **kwargs):
        super(SimpleForm, self).__init__(**kwargs)
        self.helper = FormHelper()
        if action is not None:
            if next is not None:
                action = "{}?next={}".format(action, urlquote(next))
            self.helper.form_action = action
        self.helper.add_input(Submit('submit', caption))


class SimpleModelForm(forms.ModelForm):
    """Simple model form with a helper that takes an action and a next
    parameter.
    """

    def __init__(self, caption="Submit", action="", next=None, **kwargs):
        super(SimpleModelForm, self).__init__(**kwargs)
        self.helper = FormHelper()
        if action is not None:
            if next is not None:
                action = "{}?next={}".format(action, urlquote(next))
            self.helper.form_action = action
        self.helper.add_input(Submit('submit', caption))
