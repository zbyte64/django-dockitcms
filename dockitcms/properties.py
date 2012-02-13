from dockit.schema.fields import BaseField
from dockit import Schema

from django.db.models.fields import BLANK_CHOICE_DASH

REGISTERED_BASE_SCHEMA_DESIGNS = dict()

class SchemaDesignChoiceField(BaseField):
    '''
    A choice field representing base documents that schemamaker recognizes
    The choices will be populate from two sources:
        # DocumentDesign
        # designs registered in code
    
    Schemas registered in the code have the ability to attach new functions to the document being designed
    '''
    def __init__(self, *args, **kwargs):
        super(SchemaDesignChoiceField, self).__init__(*args, **kwargs)
        self.choices = True
    
    def get_all_schemas(self):
        from models import DocumentDesign
        schemas = list()
        for document_design in DocumentDesign.objects.all():
            schemas.append(('documentdesign.%s' % document_design.pk, document_design.title, document_design.get_schema))
        for key, schema in REGISTERED_BASE_SCHEMA_DESIGNS.iteritems():
            schemas.append((key, schema._meta.verbose_name, schema))
        return schemas
    
    def get_choices(self, include_blank=True, blank_choice=BLANK_CHOICE_DASH):
        schemas = self.get_all_schemas()
        choices = list(include_blank and blank_choice or [])
        for key, label, schema in schemas:
            choices.append((key, label))
        #TODO add the ability to exclude a choice, namely so we don't have circular parentship
        return choices
    
    def get_schema(self, key):
        for skey, label, schema in self.get_all_schemas():
            if skey == key:
                if callable(schema) and not issubclass(schema, Schema):
                    schema = schema()
                return schema

