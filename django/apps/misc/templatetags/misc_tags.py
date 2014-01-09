import re

from crispy_forms.layout import Hidden
from django.template import Library, TemplateSyntaxError, Node, Variable
from django.utils.html import escape, mark_safe
from django.utils.translation import ugettext as _

from misc.forms import SimpleForm


register = Library()


@register.filter
def format(text):
    aux = escape(text)
    pat = re.compile(
        r'(^|[\n ])([\w]+?://([\w\#$%&~/.\-;:=,?@\[\]+]*))',
        re.IGNORECASE,
        )
    aux = pat.sub(
        r"\1<a class='external' href='\2' target='_blank' rel='nofollow'>\3</a>",
        aux
        )
    aux = '<p>' + aux + '</p>'
    pat = re.compile(r'(\s*\n){2,}')
    aux = pat.sub('</p><p>', aux)
    pat = re.compile(r'\n')
    aux = pat.sub('<br/>', aux)
    return mark_safe(aux)


class ModifyPathQueryNode(Node):

    def __init__(self, pairs):
        self.pairs = dict()
        for pair in pairs.split('&'):
            key, value = pair.split('=')[:2]
            self.pairs[key] = Variable(value)

    def render(self, context):
        get = context['request'].GET.copy()
        for key, value in self.pairs.items():
            get[key] = value.resolve(context)
        return context['request'].path + '?' + get.urlencode()


@register.tag
def modify_path_query(parser, token):
    try:
        tag_name, pairs = token.split_contents()
    except ValueError:
        msg = 'Bad arguments for tag "{}"'
        msg = msg.format(token.split_contents()[0])
        raise TemplateSyntaxError(msg)
    return ModifyPathQueryNode(pairs)


@register.inclusion_tag('forms/simple.html', takes_context=True)
def evaluation_form(context, item, evaluation):
    action = item.get_evaluate_url()
    next = context['request'].get_full_path()
    form = SimpleForm(caption=_(evaluation.title()), action=action, next=next)
    form.helper.add_input(Hidden('evaluation', evaluation))
    return {'form': form}

