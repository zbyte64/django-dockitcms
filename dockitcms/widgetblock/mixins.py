from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from dockitcms.mixins import BaseMixin, register_mixin
from dockitcms.models import Subsite, ViewPoint

from models import Widget, SiteWidgets

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

def get_site_widgets(site):
    entries = SiteWidgets.objects.filter(site=Site.objects.get_current())
    widgets = list()
    for entry in entries:
        widgets.extend(entry.widgets)
    return widgets

Site.widgets = property(get_site_widgets)

