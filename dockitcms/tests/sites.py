from dockitcms.models import Subsite, FilteredModelIndex
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
    
    def create_model_index(self):
        index = FilteredModelIndex(model=ContentType.objects.get_for_model(User))
        index.save()
        return index
    
    def create_subsite(self):
        Subsite.objects.index('sites').commit()
        subsite = Subsite(name='test2', url='/', sites=[Site.objects.get_current()])
        subsite.save()
        return subsite
    
    def get_view_point_kwargs(self, **kwargs):
        params = {'subsite':self.create_subsite().pk,
                  'index': self.create_model_index().pk,
                  'template_source':'html',
                  'template_html':'',
                  'url':'/',}
        params.update(kwargs)
        return params
    
    def create_view_point(self, **kwargs):
        params = self.get_view_point_kwargs()
        params.update(kwargs)
        view_point = ListViewPoint.to_python(params)
        view_point.save()
        return view_point
    
    def test_site_index(self):
        view_point = self.create_view_point()
        
        request = self.factory.get('/')
        path = '/'
        assert view_point.contains_url('/')
        
        response = self.site.index(request, path)
