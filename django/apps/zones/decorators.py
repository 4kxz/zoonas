from django.core.exceptions import PermissionDenied

from users.decorators import login_required_view


def moderator_required_view(cls):
    """Decorates `cls.dispatch` class method to require a moderator."""
    original_dispatch = cls.dispatch

    def decorated_dispatch(self, request, *args, **kwargs):
        user = request.user
        self.object = self.get_object()
        if hasattr(self.object, 'zone'):
            zone = self.object.zone
        elif hasattr(self.object, 'item'):
            # So... There are a couple of generic classes like comments
            # and reports that don't have a zone attribute.
            # However, zone admins should be allowed to do things like
            # erasing them.
            # This checks if the class has an item (that's the foreign
            # key for all the cases we ary interested in), and get its
            # zone to check the permisions.
            # This allows to use the decorator in most of those cases.
            # It's easy to make a 403 mess or leak permissions...
            # USE RESPONSIBLY.
            zone = self.object.item.zone
        else:
            raise PermissionDenied
        if user.is_superuser or zone.is_moderator(user):
            return original_dispatch(self, request, *args, **kwargs)
        else:
            raise PermissionDenied

    cls.dispatch = decorated_dispatch
    return login_required_view(cls)
