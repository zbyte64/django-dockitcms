from django.conf.urls.defaults import patterns, include, url

from dockitcms.sites import site

urlpatterns = patterns('',
    url(r'^', include(site.urls)),
)

