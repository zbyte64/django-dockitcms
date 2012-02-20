from dockitcms.mixins import BaseMixin, register_mixin

from models import Widget

import dockit

class WidgetMixin(BaseMixin):
    _widgets = dockit.ListField(dockit.SchemaField(Widget)) #TODO signal admin to exclude
    
    class MixinMeta:
        admin_display = 'object_tool'

register_mixin(WidgetMixin)

#TODO is a viewpoint mixin needed?

class WidgetViewPointMixin(object):
    pass
