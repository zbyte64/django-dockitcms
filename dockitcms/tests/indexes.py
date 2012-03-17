from dockitcms.models import FilteredCollectionIndex, CollectionFilter, CollectionParam, FilteredModelIndex, ModelFilter, ModelParam, Collection, Application
from dockitcms import fields

from dockit import schema

from django.utils import unittest
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

class IndexTest(unittest.TestCase):
    def setUp(self):
        app = Application(name='test')
        app.save()
        self.application = app
    
    def create_test_collection(self, **kwargs):
        active_mixins = kwargs.pop('active_mixins', [])
        params = {'application':self.application,
                  'key':'testcollection',
                  'title':'Test Collection',
                  'fields':[fields.CharField(name='title', null=False, blank=True),
                            fields.BooleanField(name='published', blank=True),
                            fields.BooleanField(name='featured', blank=True),],}
        params.update(kwargs)
        collection = Collection(**params)
        collection.save()
        return collection
    
    def test_filtered_collection_index(self):
        collection = self.create_test_collection()
        index = FilteredCollectionIndex(collection=collection,
                                        inclusions=[CollectionFilter(key='featured', value='true', operation='exact', value_type='boolean')],
                                        exclusions=[CollectionFilter(key='published', value='false', operation='exact', value_type='boolean')],
                                        parameters=[CollectionParam(key='title', operation='exact')],)
        index.save()
        document = collection.get_document()
        document(title='foo', published=True, featured=True).save()
        self.assertTrue(index.get_index().count())
    
    def test_filtered_model_index(self):
        index = FilteredModelIndex(model=ContentType.objects.get_for_model(User),
                                   inclusions=[ModelFilter(key='is_staff', value='true', operation='exact', value_type='boolean')],
                                   exclusions=[ModelFilter(key='is_active', value='false', operation='exact', value_type='boolean')],
                                   parameters=[ModelParam(key='username', operation='exact')],)
        index.save()
        index.get_index().count()

