from django.utils.translation import ugettext_lazy as _

from dockitcms.mixins import AdminObjectToolMixin
from dockitcms.models import Subsite, BaseViewPoint, VirtualDocumentCollection

from models import BlockWidget

from dockit import schema

class WidgetMixinSchema(schema.Schema):
    widgets = schema.ListField(schema.SchemaField(BlockWidget))
    
    class Meta:
        verbose_name = 'widget'

class WidgetMixin(AdminObjectToolMixin):
    schema_class = WidgetMixinSchema
    label = _('Widgets')

VirtualDocumentCollection.register_mixin('widgetblock.widgets', WidgetMixin)
Subsite.register_mixin('widgetblock.widgets', WidgetMixin)
BaseViewPoint.register_mixin('widgetblock.widgets', WidgetMixin)

