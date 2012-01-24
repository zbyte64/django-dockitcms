from django import forms
from django.core.files import File

from dockit.schema.fields import BaseField

from models import ThumbnailsSchema

class ThumbnailField(BaseField):
    form_field_class = forms.FileField
    
    def __init__(self, config, **kwargs):
        self.config = config
        super(ThumbnailField, self).__init__(**kwargs)
    
    def to_python(self, val, parent=None):
        if isinstance(val, File):
            schema = ThumbnailsSchema()
            schema.image = val
            schema.reprocess(self.config, force_reprocess=True)
            return schema
        return val
    
    #returns a file form field
    #to_python takes a file object and returns a ThumbnailsSchema

