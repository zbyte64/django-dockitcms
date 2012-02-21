from dockit.admin.documentadmin import DocumentAdmin, SchemaAdmin

class AdminAwareSchemaAdmin(SchemaAdmin):
    def get_form_class(self, request, obj=None):
        if hasattr(self.schema, 'get_admin_form_class'):
            form_class = self.schema.get_admin_form_class()
            if form_class:
                return form_class
        return super(AdminAwareSchemaAdmin, self).get_form_class(request, obj)
    
    def get_mixins(self, obj=None):
        if hasattr(self.schema, 'get_active_mixins'):
            return self.schema.get_active_mixins(obj)
        return []
    
    def get_object_tool_mixins(self, obj=None):
        mixins = list()
        for mixin in self.get_mixins(obj):
            if mixin.MixinMeta.admin_display == 'object_tool':
                mixins.append(mixin)
        return mixins
    
    def get_object_tools(self, request, obj=None):
        object_tools = super(AdminAwareSchemaAdmin, self).get_object_tools(request, obj)
        for mixin in self.get_object_tool_mixins(obj):
            object_tools.append(mixin.get_object_tool())
        return object_tools
    
    def get_excludes(self):
        excludes = super(AdminAwareSchemaAdmin, self).get_excludes()
        for mixin in self.get_mixins():
            if mixin.MixinMeta.admin_display in ('object_tool', 'hidden'):
                excludes.extend(mixin._meta.fields.keys())
        return excludes
    
    def get_default_inline_instances(self, exclude=[]):
        exclude = set(exclude)
        for mixin in self.get_mixins():
            if mixin.MixinMeta.admin_display in ('object_tool', 'hidden'):
                exclude.update(mixin._meta.fields.keys())
        return super(AdminAwareSchemaAdmin, self).get_default_inline_instances(exclude=exclude)

class AdminAwareDocumentAdmin(AdminAwareSchemaAdmin, DocumentAdmin):
    default_schema_admin = AdminAwareSchemaAdmin
    
    def get_admin_class_for_schema(self, schema):
        for cls, admin_class in self.schema_inlines:
            if schema == cls:
                return admin_class
        if hasattr(schema, 'get_admin_class'):
            return schema.get_admin_class()
        return self.default_schema_admin

