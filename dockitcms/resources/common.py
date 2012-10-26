from dockitresource.resources import DocumentResource

from dockitcms.signals import reload_site, post_init_applications
from dockitcms.sites import site


class ReloadCMSSiteMixin(object):
    """
    When an item belonging to this resource is modified the CMS site gets reloaded
    """
    def on_create_success(self, item):
        reload_site.send(sender=type(self), cms_site=site)
        return super(ReloadCMSSiteMixin, self).on_create_success(item)
    
    def on_update_success(self, item):
        reload_site.send(sender=type(self), cms_site=site)
        return super(ReloadCMSSiteMixin, self).on_update_success(item)
    
    def on_delete_success(self, item):
        reload_site.send(sender=type(self), cms_site=site)
        return super(ReloadCMSSiteMixin, self).on_delete_success(item)

class CMSDocumentResource(DocumentResource):
    pass
