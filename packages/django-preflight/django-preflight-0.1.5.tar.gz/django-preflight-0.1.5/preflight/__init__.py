# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from django.conf import settings

from .models import Preflight, register  # NOQA

__version__ = "0.1.5"


def autodiscover():
    """Looks for preflight.py modules in the applications."""
    # Import all preflight modules in applications
    for app_name in settings.INSTALLED_APPS:
        try:
            __import__(app_name + '.preflight', {}, {}, [''])
        except ImportError, e:
            msg = e.args[0].lower()
            if 'no module named' not in msg or 'preflight' not in msg:
                raise
