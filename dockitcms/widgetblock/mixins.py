from django.contrib.sites.models import Site

from dockitcms.mixins import BaseMixin, register_mixin
from dockitcms.models import Subsite, ViewPoint

from models import Widget, SiteWidgets

from dockit import schema

class WidgetMixin(BaseMixin):
    _widgets = schema.ListField(schema.SchemaField(Widget)) #TODO signal admin to exclude
    
    class MixinMeta:
        admin_display = 'object_tool'

register_mixin(WidgetMixin)
Subsite.register_schema_mixin(WidgetMixin)
ViewPoint.register_schema_mixin(WidgetMixin)

def get_site_widgets(site):
    entries = SiteWidgets.objects.filter(site=Site.objects.get_current())
    widgets = list()
    for entry in entries:
        widgets.extend(entry.widgets)
    return widgets

Site._widgets = property(get_site_widgets)

