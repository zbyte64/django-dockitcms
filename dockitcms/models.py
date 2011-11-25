import dockit
from dockit.backends import get_document_backend
from dockit.schema import create_document
from fieldmaker.resource import field_registry

class SchemaDefinition(dockit.Document):
    title = dockit.CharField()
    data = dockit.ListField()
    
    def get_form_specification(self):
        return field_registry.form_specifications['base.1']
    
    def get_schema_form(self):
        form_spec = self.get_form_specification()
        return form_spec.create_form(self.data)
    
    def get_schema_fields(self):
        form_spec = self.get_form_specification()
        return form_spec.get_fields(self.data)
    
    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return self.__repr__()

class Collection(dockit.Document):
    title = dockit.CharField()
    schema_definition = dockit.ReferenceField(SchemaDefinition)
    
    def save(self, *args, **kwargs):
        ret = super(Collection, self).save(*args, **kwargs)
        self.register_collection()
        return ret
    
    def register_collection(self):
        from common import dockit_field_for_form_field
        backend = get_document_backend()
        name = str(self.title) #TODO make sure it is a safe name
        form_fields = self.schema_definition.get_schema_fields()
        fields = dict()
        for key, form_field in form_fields.iteritems():
            field = dockit_field_for_form_field(form_field)
            fields[key] = field
        document = create_document(name, fields, module='dockitcms.models')
        backend.register_document(document)
    
    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return self.__repr__()

class ViewPoint(dockit.Document):
    url = dockit.CharField() #TODO middleware to hand this off
    collection = dockit.ReferenceField(Collection)
    view_class = dockit.TextField()
    view_config = dockit.DictField()
    
    def __unicode__(self):
        if self.url:
            return self.url
        else:
            return self.__repr__()
