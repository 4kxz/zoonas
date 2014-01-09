from django.template import Library
from django.utils.http import urlquote

register = Library()

@register.inclusion_tag('votes/vote_form.html', takes_context=True)
def show_vote_form(context, item, user):
    """Shows the vote form."""
    # FIXME: Move positive and negative class to article.
    request = context['request']
    next = urlquote(request.path + '?' + request.GET.urlencode())
    action = item.get_vote_url() + "?next={}".format(next)
    vote = item.get_vote(user) if user.is_authenticated() else None
    state = vote.get_description() if vote is not None else 'neutral'
    return dict(action=action, state=state)
