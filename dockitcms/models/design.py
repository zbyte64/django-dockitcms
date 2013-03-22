from dockit.schema.schema import create_schema, create_document
from dockit import schema

from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst
from django.utils.datastructures import SortedDict

from dockitcms.models.properties import SchemaDesignChoiceField

class FieldEntry(schema.Schema):
    '''
    This schema is extended by others to define a field entry
    '''
    name = schema.SlugField()
    
    field_class = None
    
    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.field_type)
    
    def get_field_kwargs(self):
        params = self.to_primitive(self)
        params.pop('field_type', None)
        params.pop('name', None)
        if params.get('verbose_name', None) == '':
            del params['verbose_name']
        kwargs = dict()
        for key, value in params.items():
            if key in self._meta.fields:
                kwargs[str(key)] = value
        return kwargs
    
    def get_field_class(self):
        return self.field_class
    
    def create_field(self):
        '''
        Returns a field for the designed schema
        '''
        kwargs = self.get_field_kwargs()
        return self.get_field_class()(**kwargs)
    
    def get_scaffold_example(self, context, varname):
        raise NotImplementedError
    
    class Meta:
        typed_field = 'field_type'

class DesignMixin(object):
    def get_fields(self):
        fields = SortedDict()
        for field_entry in self.fields:
            assert field_entry.name
            field = field_entry.create_field()
            fields[field_entry.name] = field
        return fields
    
    def get_schema_name(self):
        return 'temp_schema'
    
    def get_schema_kwargs(self, **kwargs):
        params = {'module':'dockitcms.models.virtual',
                  'virtual':True,
                  'fields':self.get_fields(),
                  'name':self.get_schema_name(),}
        attrs = {}
        if self.object_label:
            def __unicode__(instance):
                try:
                    return self.object_label % instance
                except (KeyError, TypeError):
                    return repr(instance)
            attrs['__unicode__'] = __unicode__
        params.update(kwargs)
        params.setdefault('attrs', {})
        params['attrs'].update(attrs)
        return params
    
    def get_document_kwargs(self, **kwargs):
        return self.get_schema_kwargs(**kwargs)
    
    def get_schema(self, **kwargs):
        params = self.get_schema_kwargs(**kwargs)
        return create_schema(**params)
    
    def get_document(self, **kwargs):
        params = self.get_document_kwargs(**kwargs)
        doc = create_document(**params)
        if not issubclass(doc, schema.Document):
            raise TypeError("Did not properly create a document")
        return doc

class SchemaEntry(FieldEntry, DesignMixin):
    #inherit_from = SchemaDesignChoiceField(blank=True)
    fields = schema.ListField(schema.SchemaField(FieldEntry))
    object_label = schema.CharField(blank=True)
    
    class Meta:
        proxy = True

class DocumentDesign(schema.Document, DesignMixin):
    title = schema.CharField()
    inherit_from = SchemaDesignChoiceField(blank=True)
    fields = schema.ListField(schema.SchemaField(FieldEntry), blank=True)
    object_label = schema.CharField(blank=True)
    
    def __unicode__(self):
        return self.title or ''
    
    def get_schema_name(self):
        return str(''.join([capfirst(part) for part in self.title.split()]))
    
    def get_document_kwargs(self, **kwargs):
        kwargs = DesignMixin.get_document_kwargs(self, **kwargs)
        if self.inherit_from:
            parent = self._meta.fields['inherit_from'].get_schema(self.inherit_from)
            if parent:
                if issubclass(parent, schema.Document):
                    kwargs['parents'] = (parent,)
                else:
                    kwargs['parents'] = (parent, schema.Document)
        return kwargs

