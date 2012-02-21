from dockit import schema
from dockit.views import ListView, DetailView
from dockit.backends.queryindex import QueryFilterOperation

from dockitcms.viewpoints.views import ConfigurableTemplateResponseMixin
from dockitcms.models import Collection
from dockitcms.scope import Scope

class CollectionFilter(schema.Schema):
    key = schema.CharField()
    operation = schema.CharField()
    value = schema.CharField()
    
    def get_query_filter_operation(self):
        return QueryFilterOperation(key=self.key,
                                    operation=self.operation,
                                    value=self.value)

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
        scopes.append(Scope('object', object=self.object))
        return scopes

