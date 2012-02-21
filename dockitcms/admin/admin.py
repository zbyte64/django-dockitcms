from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from django.utils.functional import update_wrapper

from dockitcms.models import Collection, ViewPoint, DocumentDesign, Subsite, Application

from views import ManageCollectionView

from common import AdminAwareDocumentAdmin

class ApplicationAdmin(AdminAwareDocumentAdmin):
    pass

admin.site.register([Application], ApplicationAdmin)

class DocumentDesignAdmin(AdminAwareDocumentAdmin):
    pass

admin.site.register([DocumentDesign], DocumentDesignAdmin)

class CollectionAdmin(AdminAwareDocumentAdmin):
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

admin.site.register([Collection], CollectionAdmin)

class SubsiteAdmin(AdminAwareDocumentAdmin):
    list_display = ['name', 'url']

admin.site.register([Subsite], SubsiteAdmin)

class ViewPointAdmin(AdminAwareDocumentAdmin):
    list_display = ['url', 'subsite', 'view_type']

admin.site.register([ViewPoint], ViewPointAdmin)
