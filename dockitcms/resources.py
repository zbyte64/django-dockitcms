from dockitresource.resources import DocumentResource
import hyperadmin


#from django.conf.urls.defaults import patterns, url
#from django.utils.functional import update_wrapper

from dockitcms.models import BaseCollection, BaseViewPoint, DocumentDesign, Subsite, Application, Index, BaseRecipe

#from views import ManageCollectionView

#from common import CMSDocumentResource, AdminAwareSchemaAdmin

class CMSDocumentResource(DocumentResource):
    pass

class ApplicationResource(CMSDocumentResource):
    pass

hyperadmin.site.register(Application, ApplicationResource)

class DocumentDesignResource(CMSDocumentResource):
    pass

hyperadmin.site.register(DocumentDesign, DocumentDesignResource)

class CollectionResource(CMSDocumentResource):
    list_display = ['title', 'application']#, 'admin_manage_link']
    
    '''
    manage_collection = ManageCollectionView
    
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
    '''

hyperadmin.site.register(BaseCollection, CollectionResource)

class IndexResource(CMSDocumentResource):
    pass

hyperadmin.site.register(Index, IndexResource)

class SubsiteResource(CMSDocumentResource):
    list_display = ['name', 'url']

hyperadmin.site.register(Subsite, SubsiteResource)

class ViewPointResource(CMSDocumentResource):
    list_display = ['base_url', 'subsite', 'view_type']

hyperadmin.site.register(BaseViewPoint, ViewPointResource)

class RecipeResource(CMSDocumentResource):
    pass

hyperadmin.site.register(BaseRecipe, RecipeResource)

