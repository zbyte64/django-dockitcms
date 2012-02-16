import dockit
from dockit.views import ListView, DetailView
from dockit.backends.queryindex import QueryFilterOperation

from dockitcms.utils import ConfigurableTemplateResponseMixin
from dockitcms.models import Collection

class CollectionFilter(dockit.Schema):
    key = dockit.CharField()
    operation = dockit.CharField()
    value = dockit.CharField()
    
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

class CollectionMixin(dockit.Schema):
    collection = dockit.ReferenceField(Collection)
    filters = dockit.ListField(dockit.SchemaField(CollectionFilter), blank=True)
    
    def get_document(self):
        return self.collection.get_document()
    
    def get_base_index(self):
        document = self.get_document()
        index = document.objects.all()
        return index_for_filters(index, self.filters)

class PointListView(ConfigurableTemplateResponseMixin, ListView):
    pass

class PointDetailView(ConfigurableTemplateResponseMixin, DetailView):
    pass

