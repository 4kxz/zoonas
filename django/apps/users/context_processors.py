

def subscribed_zone_list(request):
    if request.user.is_authenticated():
        return {'subscribed_zone_list': request.user.subscribed_zone_set.all()}
    else:
        return {}
