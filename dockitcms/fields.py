from django.contrib.contenttypes.models import ContentType

from models import SchemaEntry, FieldEntry, Collection

from dockit import schema

class BaseFieldEntry(FieldEntry):
    verbose_name = schema.CharField(blank=True, null=True)
    blank = schema.BooleanField(default=True)
    null = schema.BooleanField(default=True)
    
    default = schema.CharField(blank=True, null=True)
    help_text = schema.CharField(blank=True, null=True)
    
    scaffold_template_name = 'dockitcms/scaffold/field.html'
    
    class Meta:
        proxy = True


class ListFieldMixin(object):
    list_field_class = schema.ListField
    
    def get_list_field_kwargs(self):
        raise NotImplementedError
    
    def create_field(self):
        kwargs = self.get_list_field_kwargs()
        return self.list_field_class(**kwargs)

class BooleanField(BaseFieldEntry):
    field_class = schema.BooleanField
    
    class Meta:
        typed_key = 'BooleanField'

class CharField(BaseFieldEntry):
    field_class = schema.CharField
    
    class Meta:
        typed_key = 'CharField'

class ListCharField(ListFieldMixin, CharField):
    def get_list_field_kwargs(self):
        subfield = CharField.create_field(self)
        return {'subfield': subfield}

    class Meta:
        typed_key = 'ListCharField'

class TextField(BaseFieldEntry):
    field_class = schema.TextField
    
    class Meta:
        typed_key = 'TextField'

class ListTextField(ListFieldMixin, TextField):
    def get_list_field_kwargs(self):
        subfield = TextField.create_field(self)
        return {'subfield': subfield}

    class Meta:
        typed_key = 'ListTextField'

class ChoiceOptionSchema(schema.Schema):
    label = schema.CharField()
    value = schema.CharField()
    
    def __unicode__(self):
        return self.label

class ChoiceField(BaseFieldEntry):
    choices = schema.ListField(schema.SchemaField(ChoiceOptionSchema))
    field_class = schema.CharField
    
    def get_field_kwargs(self):
        kwargs = super(ChoiceField, self).get_field_kwargs()
        kwargs['choices'] = [(entry['value'], entry['label']) for entry in kwargs['choices']]
        return kwargs
    
    class Meta:
        typed_key = 'ChoiceField'

class ListChoiceField(ListFieldMixin, ChoiceField):
    def get_list_field_kwargs(self):
        subfield = ChoiceField.create_field(self)
        return {'subfield': subfield}

    class Meta:
        typed_key = 'ListChoiceField'

class MultipleChoiceField(ChoiceField):
    def create_field(self):
        kwargs = self.get_field_kwargs()
        return schema.ListField(self.field_class(**kwargs))
    
    class Meta:
        typed_key = 'MultipleChoiceField'

class DateField(BaseFieldEntry):
    field_class = schema.DateField
    
    class Meta:
        typed_key = 'DateField'

class ListDateField(ListFieldMixin, DateField):
    def get_list_field_kwargs(self):
        subfield = DateField.create_field(self)
        return {'subfield': subfield}

    class Meta:
        typed_key = 'ListDateField'

class DateTimeField(BaseFieldEntry):
    field_class = schema.DateTimeField
    
    class Meta:
        typed_key = 'DateTimeField'

class ListDateTimeField(ListFieldMixin, DateTimeField):
    def get_list_field_kwargs(self):
        subfield = DateTimeField.create_field(self)
        return {'subfield': subfield}

    class Meta:
        typed_key = 'ListDateTimeField'

class DecimalField(BaseFieldEntry):
    max_value = schema.IntegerField(blank=True, null=True)
    min_value = schema.IntegerField(blank=True, null=True)
    max_digits = schema.IntegerField(blank=True, null=True)
    decimal_places = schema.IntegerField(blank=True, null=True)
    
    field_class = schema.DecimalField

    class Meta:
        typed_key = 'DecimalField'

class ListDecimalField(ListFieldMixin, DecimalField):
    def get_list_field_kwargs(self):
        subfield = DecimalField.create_field(self)
        return {'subfield': subfield}

    class Meta:
        typed_key = 'ListDecimalField'

class EmailField(BaseFieldEntry):
    field_class = schema.EmailField
    
    class Meta:
        typed_key = 'EmailField'

class ListEmailField(ListFieldMixin, EmailField):
    def get_list_field_kwargs(self):
        subfield = EmailField.create_field(self)
        return {'subfield': subfield}

    class Meta:
        typed_key = 'ListEmailField'

class FileField(BaseFieldEntry):
    field_class = schema.FileField
    
    class Meta:
        typed_key = 'FileField'

class ListFileField(ListFieldMixin, FileField):
    def get_list_field_kwargs(self):
        subfield = FileField.create_field(self)
        return {'subfield': subfield}

    class Meta:
        typed_key = 'ListFileField'

class ImageField(BaseFieldEntry):
    #TODO schema.ImageField
    field_class = schema.FileField
    scaffold_template_name = 'dockitcms/scaffold/image.html'

    class Meta:
        typed_key = 'ImageField'

class ListImageField(ListFieldMixin, ImageField):
    def get_list_field_kwargs(self):
        subfield = ImageField.create_field(self)
        return {'subfield': subfield}

    class Meta:
        typed_key = 'ListImageField'

class FloatField(BaseFieldEntry):
    field_class = schema.FloatField
    #max_value = schema.IntegerField(blank=True, null=True)
    #min_value = schema.IntegerField(blank=True, null=True)
    
    class Meta:
        typed_key = 'FloatField'

class ListFloatField(ListFieldMixin, FloatField):
    def get_list_field_kwargs(self):
        subfield = FloatField.create_field(self)
        return {'subfield': subfield}

    class Meta:
        typed_key = 'ListFloatField'

class IntegerField(BaseFieldEntry):
    field_class = schema.IntegerField
    #max_value = schema.IntegerField(blank=True, null=True)
    #min_value = schema.IntegerField(blank=True, null=True)

    field_class = schema.IntegerField
    
    class Meta:
        typed_key = 'IntegerField'

class ListIntegerField(ListFieldMixin, IntegerField):
    def get_list_field_kwargs(self):
        subfield = IntegerField.create_field(self)
        return {'subfield': subfield}

    class Meta:
        typed_key = 'ListIntegerField'


class IPAddressField(BaseFieldEntry):
    field_class = schema.IPAddressField

    class Meta:
        typed_key = 'IPAddressField'

'''
class NullBooleanField(BaseField):
    field = schema.NullBooleanField

registry.register_field('NullBooleanField', NullBooleanField)
'''
'''
class RegexFieldSchema(CharFieldSchema):
    regex = schema.CharField()

class RegexField(BaseField):
    schema = RegexFieldSchema
    field = schema.RegexField

registry.register_field('RegexField', RegexField)
'''
class SlugField(BaseFieldEntry):
    field_class = schema.SlugField

    class Meta:
        typed_key = 'SlugField'

class ListSlugField(ListFieldMixin, SlugField):
    def get_list_field_kwargs(self):
        subfield = SlugField.create_field(self)
        return {'subfield': subfield}

    class Meta:
        typed_key = 'ListSlugField'

class TimeField(BaseFieldEntry):
    field_class = schema.TimeField

    class Meta:
        typed_key = 'TimeField'

class ListTimeField(ListFieldMixin, TimeField):
    def get_list_field_kwargs(self):
        subfield = TimeField.create_field(self)
        return {'subfield': subfield}

    class Meta:
        typed_key = 'ListTimeField'

'''
class URLFieldSchema(BaseFieldSchema):
    max_length = schema.IntegerField(blank=True, null=True)
    min_length = schema.IntegerField(blank=True, null=True)
    verify_exists = schema.BooleanField(initial=False)
    validator_user_agent = schema.CharField(blank=True)

class URLField(BaseField):
    form = URLFieldSchema
    field = schema.URLField

registry.register_field('URLField', URLField)
'''

class CollectionReferenceField(BaseFieldEntry):
    collection = schema.ReferenceField(Collection)

    field_class = schema.ReferenceField
    
    def get_field_kwargs(self):
        kwargs = dict(super(CollectionReferenceField, self).get_field_kwargs())
        kwargs['document'] = self.collection.get_document()
        assert issubclass(kwargs['document'], schema.Document)
        kwargs.pop('collection', None)
        return kwargs

    class Meta:
        typed_key = 'CollectionReferenceField'

class CollectionSetField(CollectionReferenceField):
    field_class = schema.DocumentSetField
    
    class Meta:
        typed_key = 'CollectionSetField'


class ModelReferenceField(BaseFieldEntry):
    model = schema.ModelReferenceField(ContentType)

    field_class = schema.ModelReferenceField
    
    def get_field_kwargs(self):
        kwargs = super(ModelReferenceField, self).get_field_kwargs()
        ct_id = kwargs.pop('model')
        if not isinstance(ct_id, (long, int)):
            model = ct_id
        else:
            model = ContentType.objects.get(pk=ct_id).model_class()
        kwargs['model'] = model
        return kwargs

    class Meta:
        typed_key = 'ModelReferenceField'

'''
class ListFieldMixin(object):
    list_field_class = schema.ListField
    
    def get_list_field_kwargs(self):
        raise NotImplementedError
    
    def create_field(self):
        kwargs = self.get_list_field_kwargs()
        return self.list_field_class(**kwargs)
'''

class ModelSetField(ModelReferenceField):
    field_class = schema.ModelSetField
    
    class Meta:
        typed_key = 'ModelSetField'

class SchemaField(SchemaEntry):
    field_class = schema.SchemaField
    scaffold_template_name = 'dockitcms/scaffold/schema.html'
    
    def get_field_kwargs(self):
        field_schema = self.get_schema()
        kwargs = {'schema':field_schema}
        return kwargs
    
    def get_scaffold_example(self, data, context, varname):
        fields = list()
        #TODO populate fields
        context['fields'] = fields
        return super(SchemaField, self).get_scaffold_example(data, context, varname)

    class Meta:
        typed_key = 'SchemaField'

class ComplexListField(SchemaEntry):
    field_class = schema.ListField
    saffold_template_name = 'dockitcms/scaffold/list.html'
    
    def get_field_kwargs(self):
        field_schema = self.get_schema()
        field_schema._meta.verbose_name = self.name
        field_schema._meta.verbose_name_plural = self.name + 's'
        kwargs = {'subfield':schema.SchemaField(field_schema)}
        return kwargs
    
    def get_scaffold_example(self, data, context, varname):
        field_schema = data.get_schema()
        #TODO
        context['subschema'] = ''
        context['subvarname'] = 'subitem'
        return super(ComplexListField, self).get_scaffold_example(data, context, varname)

    class Meta:
        typed_key = 'ComplexListField'
'''
class ListField(FieldEntry):
    subfield = schema.SchemaField(FieldEntry)
    field_class = schema.ListField
    
    def get_field_kwargs(self):
        subfield = self.subfield.create_field()
        kwargs = {'subfield':subfield}
        return kwargs

    class Meta:
        typed_key = 'ListField'
'''
