# Copyright 2014 Bevbot LLC, All Rights Reserved
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

from pykeg import EPOCH

from pykeg.backend import get_kegbot_backend
from pykeg.core import models
from pykeg.web.api.util import is_api_request

from pykeg.plugin import util as plugin_util

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse
from django.http import HttpResponseServerError
from django.template.response import SimpleTemplateResponse
from django.template import RequestContext
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)

# Requests are always allowed for these path prefixes.
PRIVACY_EXEMPT_PATHS = (
    '/account/activate/',
    '/accounts/login/',
    '/admin/',
    '/media/',
    '/setup/',
    '/sso/login',
    '/sso/logout',
)

PRIVACY_EXEMPT_PATHS += getattr(settings, 'KEGBOT_EXTRA_PRIVACY_EXEMPT_PATHS', ())


def _path_allowed(path, kbsite):
    for p in PRIVACY_EXEMPT_PATHS:
        if path.startswith(p):
            return True
    return False


class KegbotSiteMiddleware:
    ALLOWED_VIEW_MODULE_PREFIXES = (
        'pykeg.web.setup_wizard.',
    )

    def process_request(self, request):
        request.need_setup = False
        request.need_upgrade = False
        request.kbsite = None

        # Select only the `epoch` column, as pending database migrations could
        # make a full select crash.
        rows = models.KegbotSite.objects.filter(name='default').values('epoch')
        if not rows:
            request.need_setup = True
        elif rows[0].get('epoch', 0) < EPOCH:
            request.need_upgrade = True
        else:
            request.kbsite = models.KegbotSite.objects.get(name='default')
            if request.kbsite.is_setup:
                timezone.activate(request.kbsite.timezone)
                request.plugins = dict((p.get_short_name(), p) for p in plugin_util.get_plugins().values())
            else:
                request.need_setup = True

        request.backend = get_kegbot_backend()

        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        for prefix in self.ALLOWED_VIEW_MODULE_PREFIXES:
            if view_func.__module__.startswith(prefix):
                return None

        if is_api_request(request):
            # API endpoints handle "setup required" differently.
            return None

        if request.need_setup:
            return self._setup_required(request)
        elif request.need_upgrade:
            return self._upgrade_required(request)

        return None

    def _setup_required(self, request):
        if settings.EMBEDDED:
            return HttpResponseServerError('Site is not set up.', content_type='text/plain')
        return SimpleTemplateResponse('setup_wizard/setup_required.html',
            context=RequestContext(request), status=403)

    def _upgrade_required(self, request, current_epoch=None):
        if settings.EMBEDDED:
            return HttpResponseServerError('Site needs upgrade.', content_type='text/plain')
        context = RequestContext(request)
        context['current_epoch'] = current_epoch
        return SimpleTemplateResponse('setup_wizard/upgrade_required.html',
            context=context, status=403)


class HttpHostMiddleware:
    """Middleware which checks a dynamic version of settings.ALLOWED_HOSTS."""

    def process_request(self, request):
        if not getattr(request, 'kbsite', None):
            return None

        host = request.get_host()
        allowed_hosts_str = request.kbsite.allowed_hosts
        if allowed_hosts_str:
            host_patterns = allowed_hosts_str.strip().split()
        else:
            host_patterns = []
        valid = HttpHostMiddleware.validate_host(host, host_patterns)

        if not valid:
            message = "Invalid HTTP_HOST header (you may need to change Kegbot's ALLOWED_HOSTS setting): %s" % host
            if request.user.is_superuser or request.user.is_staff:
                messages.warning(request, message)
            else:
                raise SuspiciousOperation(message)

    @classmethod
    def validate_host(cls, host, allowed_hosts):
        """Clone of django.http.request.validate_host.

        Local differences: treats an empty `allowed_hosts` list as a pass.
        """
        # Validate only the domain part.
        if not allowed_hosts:
            return True

        if host[-1] == ']':
                # It's an IPv6 address without a port.
            domain = host
        else:
            domain = host.rsplit(':', 1)[0]

        for pattern in allowed_hosts:
            pattern = pattern.lower()
            match = (
                pattern == '*' or
                pattern.startswith('.') and (
                    domain.endswith(pattern) or domain == pattern[1:]
                ) or
                pattern == domain
            )
            if match:
                return True

        return False


class PrivacyMiddleware:
    """Enforces site privacy settings.

    Must be installed after ApiRequestMiddleware (in request order) to
    access is_kb_api_request attribute.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not hasattr(request, 'kbsite'):
            return None
        elif _path_allowed(request.path, request.kbsite):
            return None
        elif request.is_kb_api_request:
            # api.middleware will enforce access requirements.
            return None

        privacy = request.kbsite.privacy

        if privacy == 'public':
            return None
        elif privacy == 'staff':
            if not request.user.is_staff:
                return SimpleTemplateResponse('kegweb/staff_only.html',
                    context=RequestContext(request), status=401)
            return None
        elif privacy == 'members':
            if not request.user.is_authenticated or not request.user.is_active:
                return SimpleTemplateResponse('kegweb/members_only.html',
                    context=RequestContext(request), status=401)
            return None

        return HttpResponse('Server misconfigured, unknown privacy setting:%s' % privacy, status=500)
