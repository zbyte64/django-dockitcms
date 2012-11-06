from dockitcms.models import ModelCollection, Subsite
from dockitcms import fields
from dockitcms.viewpoints.categorypoint import CategoryViewPoint

from dockit import schema

from django.utils import unittest
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test.client import RequestFactory
from django.http import Http404

class CategoryViewPointTest(unittest.TestCase):
    def setUp(self):
        subsite = Subsite(name='test', url='/')
        subsite.save()
        self.subsite = subsite
        self.factory = RequestFactory()
    
    def create_collection(self):
        coll = ModelCollection(model=ContentType.objects.get_for_model(User))
        coll.save()
        return coll
    
    def get_view_point_kwargs(self, **kwargs):
        #TODO this is nonsensical, build out test data and make real params
        coll = self.create_collection()
        params = {'subsite':self.subsite,
                  'category_collection': coll,
                  'item_collection': coll,
                  #'item_index': coll,
                  'url':'/test/',
                  'list_template_source':'html',
                  'list_template_html':'',
                  'detail_template_source':'html',
                  'detail_template_html':'',}
        params.update(kwargs)
        return params
    
    def test_listing_view_point(self):
        view_point = CategoryViewPoint(**self.get_view_point_kwargs())
        view_point.save()
        view_point.get_urls()
        
        #request = self.factory.get('/')
        #response = view_point.dispatch(request)

    
