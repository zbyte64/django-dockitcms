from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from django.utils.functional import update_wrapper

from dockit.admin.documentadmin import DocumentAdmin

from dockitcms.models import Collection

from views import ManageCollectionView, ViewPointProxyFragmentView

class CollectionAdmin(DocumentAdmin):
    default_fragment = ViewPointProxyFragmentView
    manage_collection = ManageCollectionView
    list_display = ['title', 'admin_manage_link']
    
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

