from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator


def login_required_view(cls):
    """Decorates `cls.dispatch` class method to require login."""
    cls.dispatch = method_decorator(login_required)(cls.dispatch)
    return cls


def admin_required_view(cls):
    """Decorates `cls.dispatch` class method to require an admin."""
    original_dispatch = cls.dispatch

    def decorated_dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return original_dispatch(self, request, *args, **kwargs)
        else:
            raise PermissionDenied

    cls.dispatch = decorated_dispatch
    return login_required_view(cls)
