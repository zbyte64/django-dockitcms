from dockit.admin.documentadmin import DocumentAdmin, SchemaAdmin

class AdminAwareSchemaAdmin(SchemaAdmin):
    def __init__(self, *args, **kwargs):
        super(AdminAwareSchemaAdmin, self).__init__(*args, **kwargs)
        self.send_mixin_event('admin.init', {'admin':self})
    
    def send_mixin_event(self, event, kwargs):
        if hasattr(self.schema, 'send_mixin_event'):
            #TODO if classmethod
            return self.schema.send_mixin_event(event, kwargs)
        if hasattr(self.schema, '_collection_document'):
            return self.schema._collection_document.send_mixin_event(event, kwargs)
        return []
    
    def get_form_class(self, request, obj=None):
        if hasattr(self.schema, 'get_admin_form_class'):
            form_class = self.schema.get_admin_form_class()
            if form_class:
                return form_class
        return super(AdminAwareSchemaAdmin, self).get_form_class(request, obj)
    
    def get_object_tools(self, request, obj=None):
        object_tools = super(AdminAwareSchemaAdmin, self).get_object_tools(request, obj)
        self.send_mixin_event('admin.object_tools', 
                              {'object_tools':object_tools, 'admin':self, 'request':request, 'object':obj})
        return object_tools
    
    def get_excludes(self):
        excludes = super(AdminAwareSchemaAdmin, self).get_excludes()
        self.send_mixin_event('admin.excludes',
                              {'excludes':excludes, 'admin':self})
        return excludes
    
    def get_inline_instances(self):
        inline_instances = super(AdminAwareSchemaAdmin, self).get_inline_instances()
        self.send_mixin_event('admin.inline_instances',
                              {'inline_instances':inline_instances, 'admin':self})
        return inline_instances

class AdminAwareDocumentAdmin(AdminAwareSchemaAdmin, DocumentAdmin):
    default_schema_admin = AdminAwareSchemaAdmin
    
    def create_admin_for_schema(self, schema, obj=None):
        if obj and hasattr(obj, 'make_bound_schema'):
            schema = obj.make_bound_schema()
        return super(AdminAwareDocumentAdmin, self).create_admin_for_schema(schema, obj)
    
    def get_admin_class_for_schema(self, schema):
        for cls, admin_class in self.schema_inlines:
            if schema == cls:
                return admin_class
        if hasattr(schema, 'get_admin_class'):
            return schema.get_admin_class()
        return self.default_schema_admin

