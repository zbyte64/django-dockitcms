import dockit

MIXINS = dict()

def register_mixin(mixin_schema):
    key = mixin_schema._meta.schema_key
    MIXINS[key] = mixin_schema

def attach_mixin(mixin_schema, *schemas):
    pass

#from models import ViewPoint

class AuthMixin(dockit.Schema):
    authenticated_users_only = dockit.BooleanField(default=False)
    staff_only = dockit.BooleanField(default=False)

register_mixin(AuthMixin)
#attach_mixin(AuthMixin, ViewPoint)

class Widget(dockit.Schema):
    pass

class WidgetMixin(dockit.Schema):
    _widgets = dockit.ListField(dockit.SchemaField(Widget))
    #TODO dynamically typed schemas?

