from dockit import schema

from dockitcms.fields import BaseFieldEntry, ListFieldMixin

from models import Widget

class WidgetField(BaseFieldEntry):
    field_class = schema.SchemaField
    
    def get_field_kwargs(self):
        kwargs = dict(super(WidgetField, self).get_field_kwargs())
        kwargs['schema'] = Widget
        return kwargs
    
    class Meta:
        typed_key = 'WidgetField'

class ListWidgetField(ListFieldMixin, WidgetField):
    def get_list_field_kwargs(self):
        subfield = WidgetField.create_field(self)
        return {'subfield': subfield}

    class Meta:
        typed_key = 'ListWidgetField'

