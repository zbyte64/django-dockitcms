from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from django.utils.functional import update_wrapper

from dockitcms.models import BaseCollection, BaseViewPoint, DocumentDesign, Subsite, Application, Index

from views import ManageCollectionView

from common import AdminAwareDocumentAdmin, AdminAwareSchemaAdmin

class ApplicationAdmin(AdminAwareDocumentAdmin):
    pass

admin.site.register([Application], ApplicationAdmin)

class DocumentDesignAdmin(AdminAwareDocumentAdmin):
    pass

admin.site.register([DocumentDesign], DocumentDesignAdmin)

class CollectionSchemaAdmin(AdminAwareSchemaAdmin):
    def send_mixin_event(self, event, kwargs):
        pass #these events are meant for the collection we build

class CollectionAdmin(AdminAwareDocumentAdmin):
    default_schema_admin = CollectionSchemaAdmin
    manage_collection = ManageCollectionView
    list_display = ['title', 'application', 'admin_manage_link']
    
    def get_extra_urls(self):
        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.as_view(view, cacheable)(*args, **kwargs)
            return update_wrapper(wrapper, view)
        init = {'admin':self, 'admin_site':self.admin_site}
        return patterns('',
            url(r'^(?P<pk>.+)/manage/',
                wrap(self.manage_collection.as_view(**init)),
                name=(self.app_name+'_manage')),
        )

admin.site.register([BaseCollection], CollectionAdmin)

class IndexAdmin(AdminAwareDocumentAdmin):
    pass

admin.site.register([Index], IndexAdmin)

class SubsiteAdmin(AdminAwareDocumentAdmin):
    list_display = ['name', 'url']

admin.site.register([Subsite], SubsiteAdmin)

class ViewPointAdmin(AdminAwareDocumentAdmin):
    list_display = ['base_url', 'subsite', 'view_type']

admin.site.register([BaseViewPoint], ViewPointAdmin)
