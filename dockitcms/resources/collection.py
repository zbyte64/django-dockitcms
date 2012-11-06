from dockitcms.resources.common import CMSDocumentResource
from dockitcms.models.index import FilteredVirtualDocumentIndex, FilteredModelIndex

from hyperadmin.resources.indexes import Index
from hyperadmin.resources.models.models import ModelResource as BaseModelResource

#TODO index objects should be cached

class VirtualDocumentResource(CMSDocumentResource):
    def __init__(self, **kwargs):
        self.collection = kwargs.pop('collection')
        super(VirtualDocumentResource, self).__init__(**kwargs)
    
    def get_indexes(self):
        indexes = super(VirtualDocumentResource, self).get_indexes()
        for index in FilteredVirtualDocumentIndex.objects.filter(collection=self.collection):
            indexes[index.name] = Index(index.name, self, index.get_index())
        return indexes

class ModelResource(BaseModelResource):
    def __init__(self, **kwargs):
        self.collection = kwargs.pop('collection')
        super(ModelResource, self).__init__(**kwargs)
    
    def get_indexes(self):
        indexes = super(ModelResource, self).get_indexes()
        for index in FilteredModelIndex.objects.filter(collection=self.collection):
            indexes[index.name] = Index(index.name, self, index.get_index())
        return indexes

