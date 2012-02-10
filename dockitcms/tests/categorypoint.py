from dockitcms.viewpoints.categorypoint import CategoryViewPoint

import dockit

class CatDocument(dockit.Document):
    title = dockit.CharField()
    slug = dockit.SlugField()
    body = dockit.TextField()

CatDocument.objects.enable_index("equals", "slug", {'field':'slug'})

class ItemDocument(dockit.Document):
    title = dockit.CharField()
    slug = dockit.SlugField()
    body = dockit.TextField()
    category = dockit.ReferenceField(CatDocument)

ItemDocument.objects.enable_index("equals", "slug", {'field':'slug'})
ItemDocument.objects.enable_index("equals", "view_category", {'field':'category'})

class MockedCategoryViewPoint(CategoryViewPoint):
    category_document = None
    item_document = None
    
    def get_category_document(self):
        return self.category_document
    
    def get_item_document(self):
        return self.item_document
    
    def register_view_point(self):
        return None


from django.utils import unittest
from django.test.client import RequestFactory

class CategoryViewPointTestCase(unittest.TestCase):
    view_point_class = MockedCategoryViewPoint
    category_document = CatDocument
    item_document = ItemDocument
    
    def setUp(self):
        self.factory = RequestFactory()
        self.prep_documents()
    
    def get_view_point(self, **kwargs):
        params = self.get_view_point_kwargs()
        params.update(kwargs)
        view_point = self.view_point_class(**params)
        view_point.category_document = self.category_document
        view_point.item_document = self.item_document
        return view_point
    
    def get_view_point_kwargs(self):
        return {'url':'/',
                'category_slug_field': '', #TODO charfield to handle Nones
                'item_slug_field': '',
                'item_category_dot_path': 'category',
                'category_template_name':'dockitcms/detail.html',
                'category_template_source':'name',
                'item_template_name':'dockitcms/detail.html',
                'item_template_source':'name',}
    
    def prep_documents(self):
        self.category_document.objects.all().delete()
        cats = list()
        for i in range(5):
            data = {'title': 'title-%s' % i,
                    'slug': 'slug-%s' % i,
                    'body': 'body text'}
            cat = self.category_document(**data)
            cat.save()
            cats.append(cat)
        
        self.item_document.objects.all().delete()
        for i in range(5):
            data = {'title': 'title-%s' % i,
                    'slug': 'slug-%s' % i,
                    'body': 'body text',
                    'category': cats[i].pk,}
            self.item_document(**data).save()
    
    def test_category(self):
        view_point = self.get_view_point()
        obj = self.category_document.objects.all()[0]
        request = self.factory.get('/c/%s/' % obj.pk)
        response = view_point.dispatch(request)
        self.assertTrue('object' in response.context_data)
        self.assertEqual(response.context_data['object'], obj)
        
        self.assertTrue('item_list' in response.context_data)
        self.assertEqual(response.context_data['item_list'].count(), 1)
    
    def test_category_with_slug(self):
        view_point = self.get_view_point(category_slug_field='slug')
        obj = self.category_document.objects.all()[0]
        request = self.factory.get('/c/%s/' % obj.slug)
        response = view_point.dispatch(request)
        self.assertTrue('object' in response.context_data)
        self.assertEqual(response.context_data['object'], obj)

