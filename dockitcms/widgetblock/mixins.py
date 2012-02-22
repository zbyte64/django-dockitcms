from django.utils.translation import ugettext_lazy as _

from dockitcms.mixins import BaseMixin, register_mixin
from dockitcms.models import Subsite, ViewPoint

from models import Widget

from dockit import schema

class WidgetMixin(BaseMixin):
    widgets = schema.ListField(schema.SchemaField(Widget))
    
    class Meta:
        verbose_name = 'widget'
    
    class MixinMeta:
        admin_display = 'object_tool'

register_mixin(WidgetMixin)
Subsite.register_schema_mixin(WidgetMixin)
ViewPoint.register_schema_mixin(WidgetMixin)

