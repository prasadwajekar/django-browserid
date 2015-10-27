# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import json
import sys

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import Promise
from django.utils.six.moves.urllib.parse import urlparse

try:
    from django.utils.encoding import force_unicode as force_text
except ImportError:
    from django.utils.encoding import force_text  # Python 3


class LazyEncoder(json.JSONEncoder):
    """
    JSONEncoder that turns Promises into unicode strings to support functions
    like ugettext_lazy and reverse_lazy.
    """
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)


def import_from_setting(setting):
    """
    Attempt to load a module attribute from a module as specified by a setting.

    :raises:
        ImproperlyConfigured if anything goes wrong.
    """
    try:
        path = getattr(settings, setting)
    except AttributeError as e:
        raise ImproperlyConfigured('Setting {0} not found.'.format(setting))

    try:
        i = path.rfind('.')
        module, attr = path[:i], path[i + 1:]
    except AttributeError as e:
        raise ImproperlyConfigured('Setting {0} should be an import path.'.format(setting))

    try:
        __import__(module)
        mod = sys.modules[module]
    except ImportError as e:
        raise ImproperlyConfigured('Error importing `{0}`: {1}'.format(path, e))

    try:
        return getattr(mod, attr)
    except AttributeError as e:
        raise ImproperlyConfigured('Module {0} does not define `{1}`.'.format(module, attr))


def same_origin(url1, url2):
    """
    Checks if two URLs share the same origin, IE the same protocol,
    host, and port.
    """
    p1, p2 = urlparse(url1), urlparse(url2)
    return (p1.scheme, p1.hostname, p1.port) == (p2.scheme, p2.hostname, p2.port)
