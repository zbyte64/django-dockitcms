from dockit import schema
from dockit.backends.queryindex import QueryFilterOperation

from collection import Collection

class CollectionIndex(schema.Document):
    name = schema.CharField()
    collection = schema.ReferenceField(Collection)
    
    def get_document(self):
        return self.collection.get_document()
    
    def get_index(self):
        raise NotImplementedError
    
    def get_parameters(self):
        raise NotImplementedError
    
    class Meta:
        typed_field = 'index_type'

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

class FilteringCollectionIndex(CollectionIndex):
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
        ret = super(FilteringCollectionIndex, self).save(*args, **kwargs)
        self.get_index().commit()
        return ret
    
    class Meta:
        typed_key = 'dockitcms.filtering'

