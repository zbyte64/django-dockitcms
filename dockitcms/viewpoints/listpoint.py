from dockitcms.models import BaseViewPoint
from dockitcms.viewpoints.baseviewpoints import ListViewPoint, DetailViewPoint

from dockit import schema

from django.utils.translation import ugettext_lazy as _

class ListingViewPoint(BaseViewPoint):
    list_view = schema.SchemaField(ListViewPoint)
    detail_view = schema.SchemaField(DetailViewPoint)
    
    class Meta:
        typed_key = 'dockitcms.listing'
    
    def get_view_endpoint_definitions(self):
        endpoints = []
        endpoints.extend(self.list_view.get_view_endpoint_definitions())
        endpoints.extend(self.detail_view.get_view_endpoint_definitions())
        return endpoints

