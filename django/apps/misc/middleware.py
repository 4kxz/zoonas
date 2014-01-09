from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.http import is_safe_url


class RedirectToNext(object):

    def process_response(self, request, response):
        try:
            is_user = request.user.is_authenticated()
        except AttributeError:
            pass
        else:
            goto = response.status_code == 302
            next = request.GET.get('next')
            safe = is_safe_url(next)
            if is_user and goto and safe:
                response = HttpResponseRedirect(next)
                if settings.DEBUG:
                    print("Redirecting...")
        return response
