from dockitcms.resources.common import CMSDocumentResource
from dockitcms.models.index import FilteredVirtualDocumentIndex, FilteredModelIndex

from hyperadmin.resources.models.models import ModelResource as BaseModelResource


class CMSCollectionMixin(object):
    def __init__(self, **kwargs):
        self.collection = kwargs.pop('collection')
        self.dynamic_indexes = None
        super(CMSCollectionMixin, self).__init__(**kwargs)
    
    def get_indexes(self):
        indexes = super(CMSCollectionMixin, self).get_indexes()
        indexes.update(self.get_dynamic_indexes())
        return indexes
    
    def get_dynamic_indexes(self):
        if self.dynamic_indexes is None:
            self.dynamic_indexes = self.build_dynamic_indexes()
        return self.dynamic_indexes
    
    def build_dynamic_indexes(self):
        return {}
    
    def get_app_name(self):
        return self.collection.application.slug
    app_name = property(get_app_name)

class VirtualDocumentResource(CMSCollectionMixin, CMSDocumentResource):
    def build_dynamic_indexes(self):
        indexes = super(VirtualDocumentResource, self).build_dynamic_indexes()
        for index in FilteredVirtualDocumentIndex.objects.filter(collection=self.collection):
            indexes[index.name] = index.get_index(resource=self)
        return indexes

class ModelResource(CMSCollectionMixin, BaseModelResource):
    def build_dynamic_indexes(self):
        indexes = super(ModelResource, self).build_dynamic_indexes()
        for index in FilteredModelIndex.objects.filter(collection=self.collection):
            indexes[index.name] = index.get_index(resource=self)
        return indexes

