from django.views.generic.list import ListView

from users.decorators import admin_required_view
from .models import DomainName


# Admin views

@admin_required_view
class DomainIndexView(ListView):
    model = DomainName
    template_name = 'domains/index_page.html'
