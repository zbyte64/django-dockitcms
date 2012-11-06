from dockit import schema
from dockit.views import ListView, DetailView

from dockitcms.viewpoints.views import ConfigurableTemplateResponseMixin
from dockitcms.models import Collection
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

#TODO instead of referencing an index, reference a collection and use collection.get_resource().get_indexes() to power lookups and listings
class IndexMixin(schema.Schema):
    collection = schema.ReferenceField(Collection)
    index_name = schema.CharField()
    
    @property
    def index(self):
        return self.collection.get_resource().get_indexes()[self.index_name]
    
    def get_object_class(self):
        return self.collection.get_object_class()
    
    def get_index(self):
        return self.index.get_index_query()

class PointListView(ConfigurableTemplateResponseMixin, ListView):
    pass

class PointDetailView(ConfigurableTemplateResponseMixin, DetailView):
    def get_scopes(self):
        scopes = super(PointDetailView, self).get_scopes()
        object_scope = Scope('object', object=self.object)
        if hasattr(self.object, 'get_manage_urls'):
            manage_urls = self.object.get_manage_urls()
        else:
            manage_urls = dict()
        object_scope.add_data('object', self.object, manage_urls)
        scopes.append(object_scope)
        return scopes

TEMPLATE_SOURCE_CHOICES = [
    ('name', _('By Template Name')),
    ('html', _('By Template HTML')),
]

class TemplateMixin(schema.Schema):
    template_source = schema.CharField(choices=TEMPLATE_SOURCE_CHOICES, default='name')
    template_name = schema.CharField(default='dockitcms/list.html', blank=True)
    template_html = schema.TextField(blank=True)
    content = schema.TextField(blank=True)

class CanonicalMixin(schema.Schema):
    canonical = schema.BooleanField(help_text=_('If checked, this view point defines the canonical urls for these collections'))

