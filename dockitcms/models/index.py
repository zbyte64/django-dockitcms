from dockit import schema
from dockit.backends.queryindex import QueryFilterOperation

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from collection import Collection
from mixin import create_document_mixin

INDEX_MIXINS = {}

class Index(schema.Document, create_document_mixin(INDEX_MIXINS)):
    name = schema.CharField()
    
    def get_index(self):
        raise NotImplementedError
    
    def get_parameters(self):
        raise NotImplementedError
    
    def get_object_class(self):
        raise NotImplementedError
    
    def register_index(self):
        raise NotImplementedError
    
    class Meta:
        typed_field = 'index_type'

class CollectionIndex(Index):
    collection = schema.ReferenceField(Collection)
    
    def get_document(self):
        return self.collection.get_document()
    
    def get_object_class(self):
        return self.get_document()
    
    def register_index(self):
        self.get_index().commit()
    
    def __unicode__(self):
        return u'%s - %s' % (self.collection, self.name)
    
    class Meta:
        proxy = True

class ModelIndex(Index):
    model = schema.ModelReferenceField(ContentType)
    
    def get_model(self):
        return self.model.model_class()
    
    def get_object_class(self):
        return self.get_model()
    
    def register_index(self):
        pass
    
    def __unicode__(self):
        return u'%s - %s' % (self.model, self.name)
    
    class Meta:
        proxy = True

FILTER_OPERATION_CHOICES = [
    ('exact', 'Exact'),
]

VALUE_TYPE_CHOICES = [
    ('string', 'String'),
    ('integer', 'Integer'),
    ('boolean', 'Boolean'),
]

class CollectionFilter(schema.Schema):
    key = schema.CharField()
    operation = schema.CharField(choices=FILTER_OPERATION_CHOICES, default='exact')
    value = schema.CharField()
    value_type = schema.CharField(choices=VALUE_TYPE_CHOICES, default='string')
    
    def get_value(self):
        #TODO this is cheesy
        value = self.value
        if self.value_type == 'integer':
            value = int(value)
        elif self.value_type == 'boolean':
            value = bool(value.lower() in ('1', 'true'))
        return value
    
    def get_query_filter_operation(self):
        value = self.get_value()
        return QueryFilterOperation(key=self.key,
                                    operation=self.operation,
                                    value=value)

class CollectionParam(schema.Schema):
    key = schema.CharField()
    operation = schema.CharField(choices=FILTER_OPERATION_CHOICES, default='exact')
    
    def get_query_filter_operation(self):
        return QueryFilterOperation(key=self.key, operation=self.operation, value=None)

class FilteredCollectionIndex(CollectionIndex):
    inclusions = schema.ListField(schema.SchemaField(CollectionFilter), blank=True)
    exclusions = schema.ListField(schema.SchemaField(CollectionFilter), blank=True)
    
    parameters = schema.ListField(schema.SchemaField(CollectionParam), blank=True)
    
    def get_index(self):
        document = self.get_document()
        index = document.objects.all()
        inclusions = list()
        exclusions = list()
        params = list()
        for collection_filter in self.inclusions:
            inclusions.append(collection_filter.get_query_filter_operation())
        for collection_filter in self.exclusions:
            exclusions.append(collection_filter.get_query_filter_operation())
        for param in self.parameters:
            params.append(param.get_query_filter_operation())
        index = index._add_filter_parts(inclusions=inclusions, exclusions=exclusions, indexes=params)
        return index
    
    def save(self, *args, **kwargs):
        ret = super(FilteredCollectionIndex, self).save(*args, **kwargs)
        self.get_index().commit()
        return ret
    
    class Meta:
        typed_key = 'dockitcms.filteredcollection'

class ModelFilter(schema.Schema):
    key = schema.CharField()
    operation = schema.CharField(choices=FILTER_OPERATION_CHOICES, default='exact')
    value = schema.CharField()
    value_type = schema.CharField(choices=VALUE_TYPE_CHOICES, default='string')
    
    def get_value(self):
        #TODO this is cheesy
        value = self.value
        if self.value_type == 'integer':
            value = int(value)
        elif self.value_type == 'boolean':
            value = bool(value.lower() in ('1', 'true'))
        return value
    
    def get_query_filter_operation(self):
        value = self.get_value()
        return Q(**{'%s__%s' % (self.key, self.operation): value})

class ModelParam(schema.Schema):
    key = schema.CharField()
    operation = schema.CharField(choices=FILTER_OPERATION_CHOICES, default='exact')

class FilteredModelIndex(ModelIndex):
    inclusions = schema.ListField(schema.SchemaField(ModelFilter), blank=True)
    exclusions = schema.ListField(schema.SchemaField(ModelFilter), blank=True)
    
    parameters = schema.ListField(schema.SchemaField(ModelParam), blank=True)
    
    def get_index(self):
        model = self.get_model()
        index = model.objects.all()
        inclusions = list()
        exclusions = list()
        params = list()
        for collection_filter in self.inclusions:
            inclusions.append(collection_filter.get_query_filter_operation())
        for collection_filter in self.exclusions:
            exclusions.append(collection_filter.get_query_filter_operation())
        if inclusions:
            index = index.filter(*inclusions)
        if exclusions:
            index = index.exclude(*exclusions)
        return index
    
    class Meta:
        typed_key = 'dockitcms.filteredmodel'

