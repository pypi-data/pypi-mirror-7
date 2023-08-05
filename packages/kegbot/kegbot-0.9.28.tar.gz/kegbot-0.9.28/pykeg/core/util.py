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

"""Miscellaneous utility functions."""

# Note: imports should be limited to python stdlib, since methods here
# may be used in models.py, settings.py, etc.

import inspect
import logging
import pkgutil
import os
import pkg_resources
import requests
import sys
import tempfile
from contextlib import closing

from redis.exceptions import RedisError

from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


def get_version():
    try:
        return pkg_resources.get_distribution('kegbot').version
    except pkg_resources.DistributionNotFound:
        return 'unknown'


def get_user_agent():
    return 'KegbotServer/%s' % get_version()


def get_plugin_template_dirs(plugin_list):
    from django.utils import six
    if not six.PY3:
        fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()

    ret = []
    for plugin in plugin_list:
        plugin_module = '.'.join(plugin.split('.')[:-1])
        pkg = pkgutil.get_loader(plugin_module)
        if not pkg:
            raise ImproperlyConfigured('Cannot find plugin "%s"' % plugin)
        template_dir = os.path.join(os.path.dirname(pkg.filename), 'templates')
        if os.path.isdir(template_dir):
            if not six.PY3:
                template_dir = template_dir.decode(fs_encoding)
            ret.append(template_dir)
    return ret


def get_current_request(frames=None):
    """Walk up the stack, return the nearest first argument named "request".

    Adapted from: http://nedbatchelder.com/blog/201008/global_django_requests.html
    """
    frames = frames or inspect.stack()[1:]
    frame = None
    try:
        for f in frames:
            frame = f[0]
            code = frame.f_code
            if code.co_varnames[:1] == ("request",):
                return frame.f_locals["request"]
            elif code.co_varnames[:2] == ("self", "request",):
                return frame.f_locals["request"]
    finally:
        del frame


def download_to_tempfile(url):
    try:
        r = requests.get(url, stream=True)
        ext = os.path.splitext(url)[1]
        fd, pathname = tempfile.mkstemp(suffix=ext)
        logger.info('Downloading file %s to path %s' % (url, pathname))
        with closing(os.fdopen(fd, 'wb')):
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    os.write(fd, chunk)
        return str(pathname)
    except requests.exceptions.RequestException as e:
        raise IOError('Could not download file: {}'.format(e))


class SuppressTaskErrors(object):
    """Suppresses certain errors that occur while scheduling tasks."""

    def __init__(self, logger=None):
        self.logger = logger if logger else logging.getLogger(__name__)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        exc_info = (exc_type, exc_val, exc_tb)
        if isinstance(exc_val, RedisError):
            self.logger.error('Error scheduling task: {}'.format(exc_val),
                exc_info=exc_info)
            return True
        return False
