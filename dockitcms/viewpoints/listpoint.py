from dockitcms.models import BaseViewPoint
from dockitcms.viewpoints.baseviewpoints import ListViewPoint, DetailViewPoint

from dockit import schema

from django.utils.translation import ugettext_lazy as _

class ListingViewPoint(BaseViewPoint):
    list_view = schema.SchemaField(ListViewPoint)
    detail_view = schema.SchemaField(DetailViewPoint)
    
    class Meta:
        typed_key = 'dockitcms.listing'
    
    def register_view_endpoints(self, site):
        self.list_view.register_view_endpoints(site)
        self.detail_view.register_view_endpoints(site)

