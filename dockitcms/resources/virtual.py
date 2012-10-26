'''
Defines resources for virtual collections and applications.
Virtual resources are contained by their own resource site and is reloaded when the CMS signals an application reload
'''
from hyperadmin.resources.applications.application import ApplicationResource
from hyperadmin.resources.applications.site import SiteResource
from hyperadmin.sites import ResourceSite

from dockitcms.resources.common import CMSDocumentResource

class VirtualSiteResource(SiteResource):
    pass

class VirtualApplicationResource(ApplicationResource):
    pass

class VirtualDocumentResource(CMSDocumentResource):
    pass
    #app_name

class VirtualResourceSite(ResourceSite):
    site_resource_class = VirtualSiteResource
    application_resource_class = VirtualApplicationResource
