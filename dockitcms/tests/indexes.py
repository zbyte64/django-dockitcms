from dockitcms.models import FilteredCollectionIndex, CollectionFilter, CollectionParam, FilteredModelIndex, ModelFilter, ModelParam, Collection
from dockitcms.fields import CharField

from dockit import schema

from django.utils import unittest

class IndexTest(unittest.TestCase):
    def create_test_collection(self, **kwargs):
        active_mixins = kwargs.pop('active_mixins', [])
        params = {'application':self.application,
                  'key':'testcollection',
                  'title':'Test Collection',
                  'fields':[CharField(name='title', null=False, blank=True)],}
        params.update(kwargs)
        collection = Collection(**params)
        collection.save()
        return collection
    
    def test_filtered_collection_index(self):
        collection = self.create_test_collection()
        
