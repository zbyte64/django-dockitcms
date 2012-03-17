from dockit.admin.objecttools import ObjectTool

from django.template.loader import get_template
from django.template import Context

class MixinObjectTool(ObjectTool):
    template_name = 'dockitcms/mixin_object_tool.html'
    
    def __init__(self, mixin):
        self.mixin = mixin
    
    def render(self, request, context):
        template = get_template(self.template_name)
        context = Context(context)
        params = request.GET.copy()
        target_field = self.mixin.get_schema_class()._meta.fields.keys()[0]
        if params.get('_dotpath', False):
            params['_dotpath'] = '%s.%s' % (params['_dotpath'], target_field)
        else:
            params['_dotpath'] = target_field
        context['link_url'] = './?%s' % params.urlencode()
        context['link_display'] = self.mixin.get_object_tool_label()
        return template.render(context)

class EventRouterMixin(object):
    def __init__(self, target):
        self.target = target
    
    def handle_mixin_event(self, event, kwargs):
        attr = 'on_%s' % event.replace('.','_')
        if hasattr(self, attr):
            try:
                return getattr(self, attr)(**kwargs)
            except TypeError:
                print kwargs
                raise

class SchemaExtensionMixin(EventRouterMixin):
    schema_class = None
    
    def get_schema_class(self):
        return self.schema_class
    
    def on_document_kwargs(self, document_kwargs, **kwargs):
        schema_class = self.get_schema_class()
        document_kwargs['fields'].update(schema_class._meta.fields)
    
    def on_to_python(self, schema_class, primitive_data, parent):
        pass
    
    def on_admin_excludes(self, excludes, **kwargs):
        schema_class = self.get_schema_class()
        excludes.extend(schema_class._meta.fields.keys())
    
    def on_admin_inline_instances(self, inline_instances, **kwargs):
        schema_class = self.get_schema_class()
        for index, inline in enumerate(inline_instances):
            path = inline.dotpath.split('.')[0]
            for field_name in schema_class._meta.fields.iterkeys():
                if path == field_name:
                    inline_instances.pop(index)
                    break

class AdminObjectToolMixin(SchemaExtensionMixin):
    object_tool_class = MixinObjectTool
    object_tool_label = None
    
    def get_object_tool_label(self):
        if self.object_tool_label:
            return self.object_tool_label
        schema_class = self.get_schema_class()
        return u'Edit %s' % schema_class._meta.verbose_name
    
    def on_admin_object_tools(self, object_tools, **kwargs):
        object_tools.append(self.object_tool_class(self))

class AdminInlineMixin(SchemaExtensionMixin):
    def on_admin_inline_instances(self, inline_instances, **kwargs):
        pass

class AdminFormMixin(SchemaExtensionMixin):
    def on_admin_excludes(self, excludes, **kwargs):
        pass

