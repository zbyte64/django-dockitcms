from dockitcms.models import ModelCollection, Subsite, Application
from dockitcms import fields
from dockitcms.viewpoints.baseviewpoints import ListViewPoint, DetailViewPoint

from dockit import schema

from django.utils import unittest
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test.client import RequestFactory
from django.http import Http404

class ListViewPointTest(unittest.TestCase):
    def setUp(self):
        subsite = Subsite(name='test', url='/')
        subsite.save()
        app = Application(name='test', slug='test')
        app.save()
        self.app = app
        self.subsite = subsite
        self.factory = RequestFactory()
    
    def create_collection(self):
        coll = ModelCollection(model=ContentType.objects.get_for_model(User), application=self.app)
        coll.save()
        return coll
    
    def get_view_point_kwargs(self, **kwargs):
        params = {'subsite':self.subsite.pk,
                  'collection': self.create_collection().pk,
                  'url': '/users/',
                  'index_name': 'primary',
                  'template_source':'html',
                  'template_html':'',}
        params.update(kwargs)
        return params
    
    def test_list_view_point(self):
        view_point = ListViewPoint.to_python(self.get_view_point_kwargs())
        view_point.save()
        view_point.get_urls()
        ListViewPoint.get_admin_form_class()
        
        request = self.factory.get('/')
        #response = view_point.dispatch(request)
    
    def test_detail_view_point(self):
        view_point = DetailViewPoint.to_python(self.get_view_point_kwargs())
        view_point.save()
        view_point.get_urls()
        DetailViewPoint.get_admin_form_class()
        
        request = self.factory.get('/1/')
        #try:
        #    view_point.dispatch(request)
        #except Http404:
        #    pass

