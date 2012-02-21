from dockit import schema
from dockit.admin.objecttools import ObjectTool

from django.template.loader import get_template
from django.template import Context

MIXINS = dict()

def register_mixin(mixin_schema):
    key = mixin_schema._meta.schema_key
    MIXINS[key] = mixin_schema

def attach_mixin(mixin_schema, *schemas):
    pass

class MixinObjectTool(ObjectTool):
    template_name = 'dockitcms/mixin_object_tool.html'
    
    def __init__(self, mixin):
        self.mixin = mixin
    
    def render(self, request, context):
        template = get_template(self.template_name)
        context = Context(context)
        params = request.GET.copy()
        target_field = self.mixin._meta.fields.keys()[0]
        if '_dotpath' in params:
            params['_dotpath'] = '%s.%s' % (params['_dotpath'], target_field)
        else:
            params['_dotpath'] = target_field
        context['link_url'] = './?%s' % params.urlencode()
        context['link_display'] = 'Edit %s' % self.mixin._meta.verbose_name
        return template.render(context)

class BaseMixin(schema.Schema):
    object_tool_class = MixinObjectTool
    
    @classmethod
    def get_object_tool(cls):
        return cls.object_tool_class(cls)
    
    class MixinMeta:
        admin_display = 'hidden'

class AuthMixin(BaseMixin):
    authenticated_users_only = schema.BooleanField(default=False)
    staff_only = schema.BooleanField(default=False)
    
    class MixinMeta:
        admin_display = 'form'

register_mixin(AuthMixin)
#from models import ViewPoint
#attach_mixin(AuthMixin, ViewPoint)

#TODO roll widget buckets in, this will power much of the layout

'''
1) Collection will need to see what the active mixins are and their fields
2) Send a warning if there are any overlapping fields
3) Mixin to define admin handling, whether to be displayed in the form, as an object tool link, or hidden 
** Perhaps a new options class
** New options class may also be made for collection?

CONSIDER: what of mixins that require configuration? does such a thing exist?

'''

