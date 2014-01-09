from django.template import Library

from ..forms import RevokePermissionForm, SubscriptionForm

register = Library()


@register.inclusion_tag('forms/simple.html', takes_context=True)
def subscription_form(context, zone):
    user = context['request'].user
    if user.is_authenticated():
        add = not zone.is_subscriber(user)
        next = context['request'].get_full_path()
        form = SubscriptionForm(zone=zone, add=add, next=next)
        return {'form': form}
    else:
        return {'form': None}


class RevokePermissionStruct:
    """Struct with a permission and a RevokePermissionForm."""

    def __init__(self, perm):
        self.perm = perm
        self.form = RevokePermissionForm(zone=perm.zone, user=perm.user)


@register.inclusion_tag('zones/moderators_table.html', takes_context=True)
def revoke_permission_form(context, zone):
    aux = [RevokePermissionStruct(perm) for perm in zone.permissions()]
    return {'revoke_permissions': aux}
