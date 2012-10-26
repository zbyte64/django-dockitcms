from django.conf.urls.defaults import patterns, include, url

from dockitcms.resources.virtual import site

site.load_site()

urlpatterns = patterns('',
    url(r'', include(site.urls)),
)

import dockitcms.resources.listeners
