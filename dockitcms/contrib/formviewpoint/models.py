from dockit import schema

#TODO create view point that allows a form to be configured, a collection to be associated, and on form valid save a new record in the collection

class BaseField(schema.Schema):
    name = schema.SlugField()
    required = schema.BooleanField(default=True)
    label = schema.CharField(blank=True)
    initial = schema.CharField(blank=True)
    help_text = schema.CharField(blank=True)
    
    class Meta:
        typed_field = 'field_type'
