from dockitresource.resources import DocumentResource

from dockitcms.signals import reload_site, post_init_applications


class ReloadCMSSiteMixin(object):
    def on_create_success(self, item):
        #reload_site.send(sender=None, cms_site=None)
        return super(ReloadCMSSiteMixin, self).on_create_success(item)
    
    def on_update_success(self, item):
        #reload_applications.send(sender=None, cms_site=None)
        return super(ReloadCMSSiteMixin, self).on_update_success(item)
    
    def on_delete_success(self, item):
        #reload_applications.send(sender=None, cms_site=None)
        return super(ReloadCMSSiteMixin, self).on_delete_success(item)

class CMSDocumentResource(DocumentResource):
    pass
