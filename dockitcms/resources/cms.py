import hyperadmin

from dockitcms.models import Collection, PublicResource as ConfiguredPublicResource, DocumentDesign, Subsite, Application, Index
from dockitcms.resources.common import ReloadCMSSiteMixin, CMSDocumentResource, ReloadCMSDotpathResource


app_name = 'dockitcms'

class ApplicationResource(CMSDocumentResource):
    list_display = ['name', 'slug']

hyperadmin.site.register(Application, ApplicationResource, app_name=app_name)

class DocumentDesignResource(CMSDocumentResource):
    dotpath_resource_class = ReloadCMSDotpathResource

hyperadmin.site.register(DocumentDesign, DocumentDesignResource, app_name=app_name)

class CollectionResource(ReloadCMSSiteMixin, CMSDocumentResource):
    list_display = ['title', 'application', 'key']
    dotpath_resource_class = ReloadCMSDotpathResource

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
    dotpath_resource_class = ReloadCMSDotpathResource

hyperadmin.site.register(Index, IndexResource, app_name=app_name)

class SubsiteResource(ReloadCMSSiteMixin, CMSDocumentResource):
    list_display = ['name', 'url', 'slug']
    dotpath_resource_class = ReloadCMSDotpathResource

hyperadmin.site.register(Subsite, SubsiteResource, app_name=app_name)

class PublicResource(ReloadCMSSiteMixin, CMSDocumentResource):
    list_display = ['name', 'subsite', 'collection', 'url']
    dotpath_resource_class = ReloadCMSDotpathResource

    def get_prompt(self):
        return 'Public Resource'

hyperadmin.site.register(ConfiguredPublicResource, PublicResource, app_name=app_name)
