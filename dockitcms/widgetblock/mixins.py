from dockitcms.mixins import BaseMixin, register_mixin
from dockitcms.models import Subsite, ViewPoint


from models import Widget

import dockit

class WidgetMixin(BaseMixin):
    _widgets = dockit.ListField(dockit.SchemaField(Widget)) #TODO signal admin to exclude
    
    class MixinMeta:
        admin_display = 'object_tool'

register_mixin(WidgetMixin)
Subsite.register_schema_mixin(WidgetMixin)
ViewPoint.register_schema_mixin(WidgetMixin)


#TODO is a viewpoint mixin needed?

class WidgetViewPointMixin(object):
    pass

#viewpoint.register_mixin(WidgetViewPointMixin)

#TODO mixin viewpoint schema
#TODO mixin subsite schema

'''

ViewPoints:
    ideally prompt for mixins -> tricky as mixins may want to extend the view point schema
    
    Two tiers of mixins:
    1) global, may add fields & functions (widgets)
    2) per view point, may only add functions (auth, languages, etc)

viewpoint.register_schema_mixin(schema)
viewpoint.register_view_mixin(mixin_def)
subsite.register_schema_mixin(schema)

CONSIDER: simply registering fields in the base schema does not extend to all inheritted schemas!
Admin could use a class based method, get_mixins() to get a set of mixins. This implementation would assume the schema does not know of mixins (faily clean I would say)
* admin views confusion? get_field => None; schema admin would absorb functionality? but this assumes fragment mixin functionality. 
get_field(schema, dotpath, obj=None)
field will be the entry point for that mixin, assumed to be the first field registered to the mixin
###get_active_mixins(self) => mixin enabling managed by the document, get_field will power it off obj. Does this violate temp document pattern (yes)?
schema.get_active_mixins(cls, instance=None) =>

Alternatively could make fields an inheritable dictionary, but this breaks some contracts for the contribute to class functionality (newly added fields would not be contributed to the inheriting class)


ALTERNATIVE?

when creating a view point the schema is generated, this is bad as we are saying a particular field determines other fields
* more admin cruft
* similar to typed_field
* This may be worked into a round 2?

'''
