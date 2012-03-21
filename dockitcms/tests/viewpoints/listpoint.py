from dockitcms.models import FilteredModelIndex, Subsite
from dockitcms import fields
from dockitcms.viewpoints.listpoint import ListingViewPoint

from dockit import schema

from django.utils import unittest
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test.client import RequestFactory
from django.http import Http404

class ListingViewPointTest(unittest.TestCase):
    def setUp(self):
        subsite = Subsite(name='test', url='/')
        subsite.save()
        self.subsite = subsite
        self.factory = RequestFactory()
    
    def create_model_index(self):
        index = FilteredModelIndex(model=ContentType.objects.get_for_model(User))
        index.save()
        return index
    
    def get_view_point_kwargs(self, **kwargs):
        params = {'subsite':self.subsite.pk,
                  'index': self.create_model_index().pk,
                  'list_template_source':'html',
                  'list_template_html':'',
                  'detail_template_source':'html',
                  'detail_template_html':'',}
        params.update(kwargs)
        return params
    
    def test_listing_view_point(self):
        view_point = ListingViewPoint.to_python(self.get_view_point_kwargs())
        view_point.save()
        view_point.get_urls()
        ListingViewPoint.get_admin_form_class()
        
        request = self.factory.get('/')
        response = view_point.dispatch(request)

