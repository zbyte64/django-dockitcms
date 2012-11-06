from django.conf.urls.defaults import patterns, include, url

from dockitcms.sites import site
from dockitcms.clients import CMSClient
from dockitcms.resources.virtual import site as admin_site

admin_site.load_site()
admin_client = CMSClient(api_endpoint=admin_site, name='cmsadmin')

urlpatterns = patterns('',
    url(r'', include(site.urls)),
    url(r'^cmsapi/', include('dockitcms.resources.urls')),
    url(r'^cmsadmin/', include(admin_client.urls)),
)

