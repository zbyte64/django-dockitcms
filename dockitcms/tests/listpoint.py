from dockitcms.viewpoints.listpoint import ListViewPoint

import dockit

class SampleDocument(dockit.Document):
    title = dockit.CharField()
    slug = dockit.SlugField()
    body = dockit.TextField()

class MockedListViewPoint(ListViewPoint):
    document = None
    
    def get_document(self):
        return self.document


from django.utils import unittest
from django.test.client import RequestFactory

class ListViewPointTestChase(unittest.TestCase):
    view_point_class = MockedListViewPoint
    document = SampleDocument
    
    def setUp(self):
        self.factory = RequestFactory()
        self.view_point = self.view_point_class(**self.get_view_point_kwargs())
        self.view_point.document = self.document
        self.view_point.register_view_point()
        self.prep_documents()
    
    def get_view_point_kwargs(self):
        return {'url':'/',
                'list_template_name':'dockitcms/list.html',
                'list_template_source':'name',
                'detail_template_name':'dockitcms/detail.html',
                'detail_template_source':'name',}
    
    def prep_documents(self):
        for i in range(5):
            data = {'title': 'title-%s' % i,
                    'slug': 'slug-%s' % i,
                    'bodoy': 'body text'}
            self.document(**data).save()
    
    def test_index(self):
        request = self.factory.get('/')
        response = self.view_point.dispatch(request)
        self.assertTrue('object_list' in response.context_data)
        self.assertEqual(response.context_data['object_list'].count(), 5)
    
    def test_detail(self):
        pass

