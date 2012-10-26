import hyperadmin


#from django.conf.urls.defaults import patterns, url
#from django.utils.functional import update_wrapper

from dockitcms.models import BaseCollection, BaseViewPoint, DocumentDesign, Subsite, Application, Index, BaseRecipe
from dockitcms.resources.common import ReloadCMSSiteMixin, CMSDocumentResource
from dockitcms.resources.virtual import VirtualDocumentResource

#from views import ManageCollectionView

#from common import CMSDocumentResource, AdminAwareSchemaAdmin

class ApplicationResource(CMSDocumentResource):
    pass

hyperadmin.site.register(Application, ApplicationResource)

class DocumentDesignResource(CMSDocumentResource):
    pass

hyperadmin.site.register(DocumentDesign, DocumentDesignResource)

class CollectionResource(ReloadCMSSiteMixin, CMSDocumentResource):
    list_display = ['title', 'application']#, 'admin_manage_link']
    
    def get_manage_collection_resource_kwargs(self, item, **kwargs):
        document_class = item.instance.get_document()
        params = {'resource_adaptor':document_class,
                  'site':self.site,
                  'parent_resource':self,}
        params.update(kwargs)
        return params
    
    def get_manage_collection_resource_class(self):
        return VirtualDocumentResource
    
    def get_manage_collection_resource(self, item, **kwargs):
        kwargs = self.get_manage_collection_resource_kwargs(item, **kwargs)
        klass = self.get_manage_collection_resource_class()
        return klass(**kwargs)
    
    def register_new_collection(self, item):
        #resource = self.get_manage_collection_resource(item)
        #register app
        #register resource
        document_class = item.instance.get_document()
        self.site.register(document_class, self.get_manage_collection_resource_class())
        #perhaps we should register to a different admin?
    
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

class IndexResource(ReloadCMSSiteMixin, CMSDocumentResource):
    pass

hyperadmin.site.register(Index, IndexResource)

class SubsiteResource(ReloadCMSSiteMixin, CMSDocumentResource):
    list_display = ['name', 'url']

hyperadmin.site.register(Subsite, SubsiteResource)

class ViewPointResource(ReloadCMSSiteMixin, CMSDocumentResource):
    list_display = ['base_url', 'subsite', 'view_type']

hyperadmin.site.register(BaseViewPoint, ViewPointResource)

class RecipeResource(CMSDocumentResource):
    pass

hyperadmin.site.register(BaseRecipe, RecipeResource)

