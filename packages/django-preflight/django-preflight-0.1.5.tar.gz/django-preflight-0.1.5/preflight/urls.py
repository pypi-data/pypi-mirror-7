# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'preflight.views',
    url(r'^$', 'overview', name='preflight-overview'),
)
