from dockit.schema.fields import TypedSchemaField

from dockitcms.common import REGISTERED_VIEW_POINTS

class GenericViewPointEntryField(TypedSchemaField):
    def __init__(self, schemas=REGISTERED_VIEW_POINTS, field_name='view_type', **kwargs):
        super(GenericViewPointEntryField, self).__init__(schemas, field_name, **kwargs)
    
    def lookup_schema(self, key):
        return self.schemas[key].schema
    
    def get_schema_choices(self):
        keys = self.schemas.keys()
        return zip(keys, keys)
    
    def set_schema_type(self, val):
        return #this is done by the admin
    
    def is_instance(self, val):
        from models import ViewPoint
        return isinstance(val, ViewPoint)
