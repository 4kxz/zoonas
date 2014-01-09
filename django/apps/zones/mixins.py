from django.utils.translation import ugettext as _

from misc.mixins import NavigationMixin


class ZoneMixin(NavigationMixin):

    def get_navigation(self):
        user = self.request.user
        navigation = super(ZoneMixin, self).get_navigation()
        navigation[_('Frontpage')] = self.zone.get_absolute_url()
        navigation[_('Zone')] = self.zone.get_about_url()
        if user.is_superuser or self.zone.is_moderator(user):
            navigation[_('Settings')] = self.zone.get_settings_url()
        return navigation

    def get_action(self):
        return (_('Share'), self.zone.get_submit_url())

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(ZoneMixin, self).get_context_data(**kwargs)
        context['current_zone'] = self.zone
        is_moderator = self.zone.is_moderator(user)
        context['zone_moderator'] = is_moderator or user.is_superuser
        is_admin = is_moderator and self.zone.is_admin(user)
        context['zone_admin'] = is_admin or user.is_superuser
        return context

    @property
    def zone(self):
        return self.object.zone
