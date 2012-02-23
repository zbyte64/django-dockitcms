from dockit import schema
from dockit.views import ListView, DetailView
from dockit.backends.queryindex import QueryFilterOperation

from dockitcms.viewpoints.views import ConfigurableTemplateResponseMixin
from dockitcms.models import Collection
from dockitcms.scope import Scope

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

def index_for_filters(index, filters):
    inclusions = list()
    for collection_filter in filters:
        inclusions.append(collection_filter.get_query_filter_operation())
    index = index._add_filter_parts(inclusions=inclusions)
    return index

class CollectionMixin(schema.Schema):
    collection = schema.ReferenceField(Collection)
    filters = schema.ListField(schema.SchemaField(CollectionFilter), blank=True)
    
    def get_document(self):
        return self.collection.get_document()
    
    def get_base_index(self):
        document = self.get_document()
        index = document.objects.all()
        return index_for_filters(index, self.filters)

class PointListView(ConfigurableTemplateResponseMixin, ListView):
    pass

class PointDetailView(ConfigurableTemplateResponseMixin, DetailView):
    def get_scopes(self):
        scopes = super(PointDetailView, self).get_scopes()
        object_scope = Scope('object', object=self.object)
        object_scope.add_data('object', self.object, self.object.get_manage_urls())
        scopes.append(object_scope)
        return scopes

