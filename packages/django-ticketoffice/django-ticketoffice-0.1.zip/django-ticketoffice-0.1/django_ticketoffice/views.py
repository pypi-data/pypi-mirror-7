# -*- coding: utf-8 -*-
"""Views."""
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from django_ticketoffice.models import Ticket


class InvitationMixin(object):
    "Mixin that extracts `invitation` property from request."
    @property
    def invitation(self):
        try:
            return self._invitation
        except AttributeError:
            try:
                self._invitation = self.request.cache['invitation']
            except AttributeError, KeyError:
                try:
                    ticket_uuid = self.request.session['invitation']
                except KeyError:
                    messages.add_message(self.request, messages.ERROR,
                                         _('Missing invitation credentials.'))
                    raise PermissionDenied()
                try:
                    ticket = Ticket.objects.get(uuid=ticket_uuid)
                except Ticket.DoesNotExist:
                    messages.add_message(self.request, messages.ERROR,
                                         _('Invalid invitation.'))
                    raise PermissionDenied()
                if ticket.used:
                    messages.add_message(
                        self.request, messages.ERROR,
                        _('Invitation has already been used.'))
                    raise PermissionDenied()
                if ticket.expired:
                    messages.add_message(self.request, messages.ERROR,
                                         _('Invitation expired.'))
                    raise PermissionDenied()
                self._invitation = ticket
            return self._invitation
