from django import forms
from django.core.files import File
from django.contrib.admin import widgets

from dockit.schema.fields import BaseField

from models import ThumbnailsSchema

class ThumbnailField(BaseField):
    form_field_class = forms.FileField
    form_widget_class = widgets.AdminFileWidget#forms.FileInput
    subschema =  ThumbnailsSchema
    
    def __init__(self, config, **kwargs):
        self.config = config
        super(ThumbnailField, self).__init__(**kwargs)
    
    def is_instance(self, val):
        return isinstance(val, self.subschema)
    
    def to_python(self, val, parent=None):
        if isinstance(val, File):
            schema = self.subschema()
            schema.image = val
            schema.reprocess(self.config, force_reprocess=True)
            return schema
        if isinstance(val, dict):
            return self.subschema.to_python(val, parent=parent)
        return val
    
    def to_primitive(self, val):
        if val:
            return val.to_primitive(val)
    #returns a file form field
    #to_python takes a file object and returns a ThumbnailsSchema

