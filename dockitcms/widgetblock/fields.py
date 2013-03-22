from django import forms

from dockit import schema

from dockitcms.fields import BaseFieldEntry, ListFieldMixin

from dockitcms.widgetblock.models import Widget


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


class VisibleSchemaTypeField(schema.SchemaTypeField):
    form_field_class = forms.ChoiceField
    form_widget_class = forms.Select
    
    def formfield_kwargs(self, **kwargs):
        kwargs = super(VisibleSchemaTypeField, self).formfield_kwargs(**kwargs)
        kwargs['choices'] = self.get_choices()
        return kwargs

class TypedWidgetField(BaseFieldEntry):
    widget_type = VisibleSchemaTypeField(schemas=Widget._meta.fields['widget_type'].schemas)
    
    field_class = schema.SchemaField
    
    def get_field_kwargs(self):
        kwargs = dict(super(TypedWidgetField, self).get_field_kwargs())
        kwargs.pop('widget_type', None)
        kwargs['schema'] = Widget._meta.fields['widget_type'].schemas.get(self.widget_type, Widget)
        return kwargs
    
    class Meta:
        typed_key = 'TypedWidgetField'
