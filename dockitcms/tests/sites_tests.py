from dockitcms.models import Subsite, ModelCollection, Application
from dockitcms.viewpoints.baseviewpoints import ListViewPoint
from dockitcms.sites import DockitCMSSite

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.utils import unittest
from django.test.client import RequestFactory

class DockitCMSSiteTest(unittest.TestCase):
    def setUp(self):
        site = DockitCMSSite()
        self.site = site
        
        self.factory = RequestFactory()
        
        app = Application(name='test', slug='test')
        app.save()
        self.application = app
    
    def create_collection(self):
        coll = ModelCollection(model=ContentType.objects.get_for_model(User), application=self.application)
        coll.save()
        return coll
    
    def create_subsite(self, **kwargs):
        params = {'name':'test2',
                  'url':'/',
                  'sites':[Site.objects.get_current()],}
        params.update(kwargs)
        subsite = Subsite(**params)
        subsite.save()
        return subsite
    
    def get_view_point_kwargs(self, **kwargs):
        params = {'subsite':self.create_subsite(**kwargs.pop('subsite_params', {})).pk,
                  'collection': self.create_collection().pk,
                  'index_name': 'primary',
                  'template_source':'html',
                  'template_html':'',
                  'url':'/',}
        params.update(kwargs)
        return params
    
    def create_view_point(self, **kwargs):
        params = self.get_view_point_kwargs(**kwargs)
        view_point = ListViewPoint.to_python(params)
        #view_point.save()
        return view_point
    
    def test_site_index(self):
        view_point = self.create_view_point()
        
        path = '/'
        
        request = self.factory.get(path)
        #self.assertTrue(view_point.contains_url(path))
        #response = self.site.index(request, path)
    
    def test_site_index_with_suburl(self):
        view_point = self.create_view_point(subsite_params={'url':'/subsite/'})
        
        path = '/subsite/'
        
        import inspect
        
        #self.assertEqual(view_point.subsite.url, path)
        #self.assertEqual(view_point._base_url(), path, inspect.getsource(view_point._base_url))
        #self.assertEqual(view_point.base_url, path)
        
        request = self.factory.get(path)
        #self.assertTrue(view_point.contains_url(path))
        #self.assertTrue(view_point.contains_url(path+'5/'))
        #self.assertFalse(view_point.contains_url('/'))
        #response = self.site.index(request, path)

