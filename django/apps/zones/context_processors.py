from django.conf import settings

from .models import Zone


def default_zone_list(request):
    """Adds the default zones to the context."""
    zones = Zone.objects.all()[:settings.ZONE_LIST_SIZE]
    return {'default_zone_list': zones}
