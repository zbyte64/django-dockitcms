from dockit import schema
from dockit.views import ListView, DetailView

from dockitcms.viewpoints.views import ConfigurableTemplateResponseMixin
from dockitcms.models import CollectionIndex
from dockitcms.scope import Scope

from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

LIST_CONTEXT_DESCRIPTION = mark_safe(_('''
Context:<br/>
<em>object_list</em> <span>The list of items</span><br/>
<em>page</em> <span>Page object if paginate by is supplied</span><br/>
<em>paginator</em> <span>Paginator object if paginate by is supplied</span><br/>
'''))

DETAIL_CONTEXT_DESCRIPTION = mark_safe(_('''
Context:<br/>
<em>object</em> <span>The currently viewed object</span><br/>
'''))


def index_for_filters(index, filters):
    inclusions = list()
    for collection_filter in filters:
        inclusions.append(collection_filter.get_query_filter_operation())
    index = index._add_filter_parts(inclusions=inclusions)
    return index

class CollectionMixin(schema.Schema):
    index = schema.ReferenceField(CollectionIndex)
    
    def get_document(self):
        return self.index.get_document()
    
    def get_index(self):
        return self.index.get_index()

class PointListView(ConfigurableTemplateResponseMixin, ListView):
    pass

class PointDetailView(ConfigurableTemplateResponseMixin, DetailView):
    def get_scopes(self):
        scopes = super(PointDetailView, self).get_scopes()
        object_scope = Scope('object', object=self.object)
        object_scope.add_data('object', self.object, self.object.get_manage_urls())
        scopes.append(object_scope)
        return scopes

