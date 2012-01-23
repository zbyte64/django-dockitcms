from dockit.schema.fields import GenericSchemaField

from dockitcms.common import REGISTERED_VIEW_POINTS

class GenericViewPointEntryField(GenericSchemaField):
    def to_primitive(self, val):
        if hasattr(val, 'to_primitive'):
            return val.to_primitive(val)
        return super(GeneriViewPointEntryField, self).to_primitive(val)
    
    def to_python(self, val, parent=None):
        if self.is_instance(val):
            return val
        view_type = val['view_type']
        view_spec = REGISTERED_VIEW_POINTS[view_type]
        return view_spec.schema.to_python(val, parent=parent)
    
    def is_instance(self, val):
        from models import ViewPoint
        return isinstance(val, ViewPoint)
