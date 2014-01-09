from collections import OrderedDict

from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, PageNotAnInteger
from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.generic.base import ContextMixin


# TODO: WIP
class OrderedMixin(object):
    """Adds functionality to order a list of objects."""
    default_order = 'default'

    def get_order(self):
        return self.request.GET.get('sort', self.default_order)


class ItemListMixin(ContextMixin):
    """Allows to use a paginated list of objects from any model."""
    paginator_class = Paginator
    page_size = settings.SUBMISSIONS_PER_PAGE
    context_item_list_name = 'item_list'

    def get_item_list(self, **kwargs):
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        context = super(ItemListMixin, self).get_context_data(**kwargs)
        # Add paginator to context
        queryset = self.get_item_list(**kwargs)
        paginator = self.paginator_class(queryset, self.page_size)
        page_number = self.request.GET.get('page', 1)
        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            raise Http404(_('Invalid page.'))
        except InvalidPage:
            raise Http404(_('Invalid page.'))
        page_context = {
            self.context_item_list_name: page.object_list,
            'paginator': paginator,
            'page_obj': page,
            'is_paginated': page.has_other_pages(),
            }
        context.update(page_context)
        return context


class OrderedItemListMixin(ItemListMixin, OrderedMixin):

    def get_ordered_list(self, order, **args):
        raise NotImplementedError

    def get_item_list(self, **args):
        order = self.get_order()
        return self.get_ordered_list(order=order)


class NavigationMixin(object):
    section = None

    class Link:
        """Holds a link as a pair <text, url>."""

        def __init__(self, text, url=None):
            self.text = text
            self.url = url

        def __unicode__(self):
            return self.text

        def __nonzero__(self):
            return self.text is not None

        def __cmp__(self, other):
            return unicode(self) != unicode(other)

    def get_section(self):
        """Returns the current section."""
        return self.section

    def get_navigation(self):
        """Returns a `dict` of <name, url>.
        Can be empty for no navigation.
        """
        return OrderedDict()

    def get_action(self):
        """Returns a pair <name, url>. Can be empty for no action."""
        return ()

    def get_context_data(self, **kwargs):
        """Adds navigation variables to the template context."""
        context = super(NavigationMixin, self).get_context_data(**kwargs)
        index = self.get_navigation()
        if index:
            links = [NavigationMixin.Link(t, u) for t, u in index.items()]
            context['navigation'] = links
            context['section'] = self.get_section()
        action = self.get_action()
        if action:
            context['action'] = NavigationMixin.Link(*action)
        return context
