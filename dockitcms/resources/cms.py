import hyperadmin

from dockitcms.models import Collection, PublicResourceDefinition, DocumentDesign, Subsite, Application, Index
from dockitcms.resources.common import ReloadCMSSiteMixin, CMSDocumentResource


app_name = 'dockitcms'

class ApplicationResource(CMSDocumentResource):
    list_display = ['name', 'slug']

hyperadmin.site.register(Application, ApplicationResource, app_name=app_name)

class DocumentDesignResource(CMSDocumentResource):
    pass

hyperadmin.site.register(DocumentDesign, DocumentDesignResource, app_name=app_name)

class CollectionResource(ReloadCMSSiteMixin, CMSDocumentResource):
    list_display = ['title', 'application', 'key']
    
    def get_manage_collection_resource_kwargs(self, item, **kwargs):
        document_class = item.instance.get_document()
        params = {'resource_adaptor':document_class,
                  'site':self.site,
                  'parent_resource':self,
                  'collection':item,}
        params.update(kwargs)
        return params
    
    def get_manage_collection_resource(self, item, **kwargs):
        kwargs = self.get_manage_collection_resource_kwargs(item, **kwargs)
        klass = item.get_resource_class()
        return klass(**kwargs)

hyperadmin.site.register(Collection, CollectionResource, app_name=app_name)

class IndexResource(ReloadCMSSiteMixin, CMSDocumentResource):
    pass

hyperadmin.site.register(Index, IndexResource, app_name=app_name)

class SubsiteResource(ReloadCMSSiteMixin, CMSDocumentResource):
    list_display = ['name', 'url', 'slug']

hyperadmin.site.register(Subsite, SubsiteResource, app_name=app_name)

#TODO this is redundant naming
class PublicResourceDefinitionResource(ReloadCMSSiteMixin, CMSDocumentResource):
    list_display = ['name', 'subsite', 'collection', 'url']
    
    def get_prompt(self):
        return 'Public Resource'

hyperadmin.site.register(PublicResourceDefinition, PublicResourceDefinitionResource, app_name=app_name)
