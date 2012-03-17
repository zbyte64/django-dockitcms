from dockitcms.models import FilteredModelIndex, Subsite
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
        self.subsite = subsite
        self.factory = RequestFactory()
    
    def create_model_index(self):
        index = FilteredModelIndex(model=ContentType.objects.get_for_model(User))
        index.save()
        return index
    
    def get_view_point_kwargs(self):
        return {'subsite':self.subsite,
                'index': self.create_model_index(),
                'template_source':'html',
                'template_html':'',}
    
    def test_list_view_point(self):
        view_point = ListViewPoint(**self.get_view_point_kwargs())
        view_point.save()
        view_point.get_urls()
        ListViewPoint.get_admin_form_class()
        
        request = self.factory.get('/')
        response = view_point.dispatch(request)
    
    def test_detail_view_point(self):
        view_point = DetailViewPoint(**self.get_view_point_kwargs())
        view_point.save()
        view_point.get_urls()
        DetailViewPoint.get_admin_form_class()
        
        request = self.factory.get('/1/')
        try:
            view_point.dispatch(request)
        except Http404:
            pass
    
    
