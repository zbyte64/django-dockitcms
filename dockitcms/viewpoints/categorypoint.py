from dockitcms.models import ViewPoint, Collection
from dockitcms.utils import ConfigurableTemplateResponseMixin
#from dockit.forms import DocumentForm
from dockit.views import ListView, DetailView

from django.conf.urls.defaults import patterns, url
#from django import forms
#from django.template import Template, TemplateSyntaxError
from django.utils.translation import ugettext_lazy as _


import dockit

TEMPLATE_SOURCE_CHOICES = [
    ('name', _('By Template Name')),
    ('html', _('By Template HTML')),
]

class PointListView(ConfigurableTemplateResponseMixin, ListView):
    pass

class PointDetailView(ConfigurableTemplateResponseMixin, DetailView):
    pass

class CategoryDetailView(PointDetailView):
    item_collection = None
    
    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        context['item_list'] = self.item_collection.objects.filter.view_category(self.object.pk)
        return context

class ItemDetailView(PointDetailView):
    pass
    


class SingleObjectView(dockit.Schema):
    slug = dockit.SlugField()
    url_position = dockit.CharField(choices=[])
    template_source = dockit.CharField(choices=TEMPLATE_SOURCE_CHOICES, default='name')
    template_name = dockit.CharField(default='dockitcms/list.html', blank=True)
    template_html = dockit.TextField(blank=True)
    content = dockit.TextField(blank=True)


class CategoryViewPoint(ViewPoint):
    category_collection = dockit.ReferenceField(Collection)
    category_slug_field = dockit.CharField()
    category_template_source = dockit.CharField(choices=TEMPLATE_SOURCE_CHOICES, default='name')
    category_template_name = dockit.CharField(default='dockitcms/detail.html', blank=True)
    category_template_html = dockit.TextField(blank=True)
    category_content = dockit.TextField(blank=True)
    
    #additional_category_views = dockit.ListField(dockit.SchemaField(SingeObjectView))
    
    item_collection = dockit.ReferenceField(Collection)
    item_slug_field = dockit.CharField()
    item_category_dot_path = dockit.CharField()
    item_template_source = dockit.CharField(choices=TEMPLATE_SOURCE_CHOICES, default='name')
    item_template_name = dockit.CharField(default='dockitcms/detail.html', blank=True)
    item_template_html = dockit.TextField(blank=True)
    item_content = dockit.TextField(blank=True)
    
    #additional_item_views = dockit.ListField(dockit.SchemaField(SingeObjectView))
    
    category_view_class = CategoryDetailView
    item_view_class = ItemDetailView
    
    class Meta:
        typed_key = 'categoryview'
    
    def register_view_point(self):
        if self.category_slug_field:
            doc_cls = self.category_collection.get_document()
            doc_cls.objects.enable_index("equals", self.category_slug_field, {'field':self.category_slug_field})
        if self.item_slug_field:
            doc_cls = self.item_collection.get_document()
            doc_cls.objects.enable_index("equals", self.item_slug_field, {'field':self.item_slug_field})
        if self.item_category_dot_path:
            doc_cls = self.item_collection.get_document()
            #TODO need a better filter spec...
            doc_cls.objects.enable_index("equals", 'view_category', {'dotpath':self.item_category_dot_path})
    
    def get_category_document(self):
        doc_cls = self.category_collection.get_document()
        view_point = self
        class WrappedDoc(doc_cls):
            def get_absolute_url(self):
                if view_point.category_slug_field:
                    return view_point.reverse('category-detail', self[view_point.category_slug_field])
                return view_point.reverse('category-detail', self.pk)
            
            class Meta:
                proxy = True
        
        return WrappedDoc
    
    def get_item_document(self):
        doc_cls = self.item_collection.get_document()
        view_point = self
        class WrappedDoc(doc_cls):
            def get_absolute_url(self):
                if view_point.item_slug_field:
                    return view_point.reverse('item-detail', self[view_point.item_slug_field])
                return view_point.reverse('item-detail', self.pk)
            
            class Meta:
                proxy = True
        
        return WrappedDoc
    
    def _configuration_from_prefix(self, params, prefix):
        config = dict()
        for key in ('template_source', 'template_name', 'template_html', 'content'):
            config[key] = params.get('%s_%s' % (prefix, key), None)
        return config
    
    def get_urls(self):
        category_document = self.get_category_document()
        item_document = self.get_item_document()
        params = self.to_primitive(self)
        urlpatterns = patterns('',
            #url(r'^$', 
            #    self.list_view_class.as_view(document=document,
            #                          configuration=self._configuration_from_prefix(params, 'list'),
            #                          paginate_by=params.get('paginate_by', None)),
            #    name='index',
            #),
        )
        if self.category_slug_field:
            urlpatterns += patterns('',
                url(r'^c/(?P<slug>.+)/$', 
                    self.category_view_class.as_view(document=category_document,
                                            slug_field=self.category_slug_field,
                                            item_collection=item_document,
                                            configuration=self._configuration_from_prefix(params, 'category'),),
                    name='category-detail',
                ),
            )
        else:
            urlpatterns += patterns('',
                url(r'^c/(?P<pk>.+)/$', 
                    self.category_view_class.as_view(document=category_document,
                                            item_collection=item_document,
                                            configuration=self._configuration_from_prefix(params, 'category'),),
                    name='category-detail',
                ),
            )
        if self.item_slug_field:
            urlpatterns += patterns('',
                url(r'^i/(?P<slug>.+)/$', 
                    self.item_view_class.as_view(document=item_document,
                                            slug_field=self.item_slug_field,
                                            configuration=self._configuration_from_prefix(params, 'item'),),
                    name='item-detail',
                ),
            )
        else:
            urlpatterns += patterns('',
                url(r'^i/(?P<pk>.+)/$', 
                    self.item_view_class.as_view(document=item_document,
                                            configuration=self._configuration_from_prefix(params, 'item'),),
                    name='item-detail',
                ),
            )
        return urlpatterns

