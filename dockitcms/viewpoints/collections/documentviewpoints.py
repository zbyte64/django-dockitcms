from dockitcms.viewpoints.forms import TemplateFormMixin

from dockitcms.utils import ConfigurableTemplateResponseMixin
from dockitcms.models import ViewPoint, Collection

import dockit
from dockit.forms import DocumentForm
from dockit.views import ListView, DetailView
from dockit.backends.queryindex import QueryFilterOperation

from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext_lazy as _


TEMPLATE_SOURCE_CHOICES = [
    ('name', _('By Template Name')),
    ('html', _('By Template HTML')),
]

class PointListView(ConfigurableTemplateResponseMixin, ListView):
    pass

class PointDetailView(ConfigurableTemplateResponseMixin, DetailView):
    pass

class CollectionFilter(dockit.Schema):
    field = dockit.CharField()
    operation = dockit.CharField()
    value = dockit.CharField()
    
    def get_query_filter_operation(self):
        return QueryFilterOperation(field=self.field,
                                    operation=self.operation,
                                    value=self.value)

class BaseCollectionViewPoint(ViewPoint):
    collection = dockit.ReferenceField(Collection)
    template_source = dockit.CharField(choices=TEMPLATE_SOURCE_CHOICES, default='name')
    template_name = dockit.CharField(default='dockitcms/list.html', blank=True)
    template_html = dockit.TextField(blank=True)
    content = dockit.TextField(blank=True)
    filters = dockit.ListField(dockit.SchemaField(CollectionFilter), blank=True)
    
    view_class = None
    
    class Meta:
        proxy = True
    
    @classmethod
    def get_admin_form_class(cls):
        return BaseCollectionViewPointForm
    
    def get_document(self):
        return self.collection.get_document()
    
    def get_base_index(self):
        document = self.get_document()
        index = document.objects.all()
        inclusions = list()
        for collection_filter in self.filters:
            inclusions.append(collection_filter.get_query_filter_operation())
        index = index._add_filter_parts(inclusions=inclusions)
        return index
    
    def register_view_point(self):
        index = self.get_base_index()
        index.commit()

class CollectionListViewPoint(BaseCollectionViewPoint):
    paginate_by = dockit.IntegerField(blank=True, null=True)
    #TODO order by
    
    view_class = PointListView
    
    def get_urls(self):
        params = self.to_primitive(self)
        document = self.get_document()
        index = self.get_base_index()
        urlpatterns = patterns('',
            url(r'^$', 
                self.view_class.as_view(document=document,
                                      queryset=index,
                                      configuration=params,
                                      paginate_by=self.paginate_by),
                name='index',
            ),
        )
        return urlpatterns
    
    class Meta:
        typed_key = 'dockitcms.collectionlistview'

class CollectionDetailViewPoint(BaseCollectionViewPoint):
    slug_field = dockit.SlugField(blank=True)
    
    view_class = PointDetailView
    
    def get_base_index(self):
        index = super(CollectionDetailViewPoint, self).get_base_index()
        if self.slug_field:
            index = index.index(self.slug_field)
        return index
    
    def get_urls(self):
        params = self.to_primitive(self)
        document = self.get_document()
        index = self.get_base_index()
        if self.slug_field:
            return patterns('',
                url(r'^(?P<slug>.+)/$',
                    self.view_class.as_view(document=document,
                                          queryset=index,
                                          configuration=params,
                                          slug_field=self.slug_field,),
                    name='index',
                ),
            )
        else:
            return patterns('',
                url(r'^(?P<pk>.+)/$',
                    self.view_class.as_view(document=document,
                                          queryset=index,
                                          configuration=params,),
                    name='index',
                ),
            )
    
    class Meta:
        typed_key = 'dockitcms.collectiondetailview'

class BaseCollectionViewPointForm(TemplateFormMixin, DocumentForm):
    class Meta:
        document = BaseCollectionViewPoint

