from dockitcms.viewpoints.listpoint import ListViewPoint

import dockit

class SampleDocument(dockit.Document):
    title = dockit.CharField()
    slug = dockit.SlugField()
    body = dockit.TextField()

SampleDocument.objects.enable_index("equals", "slug", {'field':'slug'})

class MockedListViewPoint(ListViewPoint):
    document = None
    
    def get_document(self):
        return self.document
    
    def register_view_point(self):
        return None


from django.utils import unittest
from django.test.client import RequestFactory

class ListViewPointTestCase(unittest.TestCase):
    view_point_class = MockedListViewPoint
    document = SampleDocument
    
    def setUp(self):
        self.factory = RequestFactory()
        self.prep_documents()
    
    def get_view_point(self, **kwargs):
        params = self.get_view_point_kwargs()
        params.update(kwargs)
        view_point = self.view_point_class(**params)
        view_point.document = self.document
        return view_point
    
    def get_view_point_kwargs(self):
        return {'url':'/',
                'slug_field': '', #TODO charfield to handle Nones
                'list_template_name':'dockitcms/list.html',
                'list_template_source':'name',
                'detail_template_name':'dockitcms/detail.html',
                'detail_template_source':'name',}
    
    def prep_documents(self):
        self.document.objects.all().delete()
        for i in range(5):
            data = {'title': 'title-%s' % i,
                    'slug': 'slug-%s' % i,
                    'body': 'body text'}
            self.document(**data).save()
    
    def test_index(self):
        view_point = self.get_view_point()
        request = self.factory.get('/')
        response = view_point.dispatch(request)
        self.assertTrue('object_list' in response.context_data)
        self.assertEqual(response.context_data['object_list'].count(), 5)
    
    def test_detail(self):
        view_point = self.get_view_point()
        obj = self.document.objects.all()[0]
        request = self.factory.get('/%s/' % obj.pk)
        response = view_point.dispatch(request)
        self.assertTrue('object' in response.context_data)
        self.assertEqual(response.context_data['object'], obj)
    
    def test_detail_with_slug(self):
        view_point = self.get_view_point(slug_field='slug')
        obj = self.document.objects.all()[0]
        request = self.factory.get('/%s/' % obj.slug)
        response = view_point.dispatch(request)
        self.assertTrue('object' in response.context_data)
        self.assertEqual(response.context_data['object'], obj)

