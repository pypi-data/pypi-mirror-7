#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Zuza Software Foundation
#
# This file is part of Pootle.
#
# Pootle is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# Pootle is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Pootle; if not, see <http://www.gnu.org/licenses/>.

from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext as _


class SuperuserRequiredMixin(object):
    """Require users to have the `is_superuser` bit set."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            msg = _('You do not have rights to administer Pootle.')
            raise PermissionDenied(msg)

        return super(SuperuserRequiredMixin, self) \
                .dispatch(request, *args, **kwargs)
