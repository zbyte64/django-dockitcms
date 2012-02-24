from dockitcms.models import ViewPoint, Collection
from dockitcms.viewpoints.common import CanonicalMixin, TEMPLATE_SOURCE_CHOICES
from dockitcms.scope import Scope
#from schema.forms import DocumentForm

from django.conf.urls.defaults import patterns, url
#from django import forms
#from django.template import Template, TemplateSyntaxError
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from common import PointListView, PointDetailView, CollectionFilter, index_for_filters

from dockit import schema

class CategoryDetailView(PointListView):
    items_for_category_index = None
    item_category_dot_path = None
    category = None
    slug_field = None
    
    
    def get_category(self):
        if not self.category:
            if 'slug' in self.kwargs:
                self.category = self.document.objects.get(**{self.slug_field:self.kwargs['slug']})
            else:
                self.category = self.document.objects.get(pk=self.kwargs['pk'])
        return self.category
    
    def get_queryset(self):
        category = self.get_category()
        return self.items_for_category_index.filter(**{self.item_category_dot_path: category.pk})
    
    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context
    
    def get_scopes(self):
        scopes = super(PointListView, self).get_scopes()
        category = self.get_category()
        object_scope = Scope('object', object=category)
        object_scope.add_data('object', category, category.get_manage_urls())
        scopes.append(object_scope)
        return scopes

class ItemDetailView(PointDetailView):
    pass

CATEGORY_CONTEXT_DESCRIPTION = mark_safe('''
Context:<br/>
<em>category</em> <span>The category object</span><br/>
<em>object_list</em> <span>The list of items belonging to the category</span>

''')

ITEM_CONTEXT_DESCRIPTION = mark_safe('''
Context: <br/>
<em>object</em> <span>The item object</span>
''')

class CategoryViewPoint(ViewPoint, CanonicalMixin):
    category_collection = schema.ReferenceField(Collection)
    category_slug_field = schema.CharField(blank=True)
    category_template_source = schema.CharField(choices=TEMPLATE_SOURCE_CHOICES, default='name')
    category_template_name = schema.CharField(default='dockitcms/detail.html', blank=True)
    category_template_html = schema.TextField(blank=True)
    category_content = schema.TextField(blank=True, help_text=CATEGORY_CONTEXT_DESCRIPTION)
    category_filters = schema.ListField(schema.SchemaField(CollectionFilter), blank=True)
    
    item_collection = schema.ReferenceField(Collection)
    item_slug_field = schema.CharField(blank=True)
    item_category_dot_path = schema.CharField()
    item_template_source = schema.CharField(choices=TEMPLATE_SOURCE_CHOICES, default='name')
    item_template_name = schema.CharField(default='dockitcms/detail.html', blank=True)
    item_template_html = schema.TextField(blank=True)
    item_content = schema.TextField(blank=True, help_text=ITEM_CONTEXT_DESCRIPTION)
    item_filters = schema.ListField(schema.SchemaField(CollectionFilter), blank=True)
    
    category_view_class = CategoryDetailView
    item_view_class = ItemDetailView
    
    class Meta:
        typed_key = 'dockitcms.collectioncategoryview'
    
    def get_category_index(self):
        document = self.get_category_document()
        index = document.objects.all()
        if self.category_slug_field:
            index = index.index(self.category_slug_field)
        return index_for_filters(index, self.category_filters)
        
    def get_item_index(self):
        document = self.get_item_document()
        index = document.objects.all()
        if self.item_slug_field:
            index = index.index(self.item_slug_field)
        return index_for_filters(index, self.item_filters)
    
    def get_items_for_category_index(self):
        document = self.get_item_document()
        index = document.objects.all()
        index = index.index(self.item_category_dot_path)
        return index 
    
    def register_view_point(self):
        self.get_category_index().commit()
        self.get_item_index().commit()
        self.get_items_for_category_index().commit()
    
    def get_category_document(self):
        doc_cls = self.category_collection.get_document()
        view_point = self
        
        def get_absolute_url_for_instance(instance):
            if view_point.category_slug_field:
                return view_point.reverse('category-detail', instance[view_point.category_slug_field])
            return view_point.reverse('category-detail', instance.pk)
        
        if self.canonical:
            setattr(doc_cls, 'get_absolute_url', get_absolute_url_for_instance)
            #doc_cls.get_absolute_url = get_absolute_url_for_instance
        
        class WrappedDoc(doc_cls):
            get_absolute_url = get_absolute_url_for_instance
            
            class Meta:
                proxy = True
        
        return WrappedDoc
    
    def get_item_document(self):
        doc_cls = self.item_collection.get_document()
        view_point = self
        
        def get_absolute_url_for_instance(instance):
            if view_point.item_slug_field:
                return view_point.reverse('item-detail', instance[view_point.item_slug_field])
            return view_point.reverse('item-detail', instance.pk)
        
        if self.canonical:
            doc_cls.get_absolute_url = get_absolute_url_for_instance
        
        class WrappedDoc(doc_cls):
            get_absolute_url = get_absolute_url_for_instance
            
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
        category_index = self.get_category_index()
        item_index = self.get_item_index()
        items_for_category_index = self.get_items_for_category_index()
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
                                            queryset=category_index,
                                            view_point=self,
                                            item_category_dot_path=self.item_category_dot_path,
                                            items_for_category_index=items_for_category_index,
                                            configuration=self._configuration_from_prefix(params, 'category'),),
                    name='category-detail',
                ),
            )
        else:
            urlpatterns += patterns('',
                url(r'^c/(?P<pk>.+)/$', 
                    self.category_view_class.as_view(document=category_document,
                                            queryset=category_index,
                                            view_point=self,
                                            item_category_dot_path=self.item_category_dot_path,
                                            items_for_category_index=items_for_category_index,
                                            configuration=self._configuration_from_prefix(params, 'category'),),
                    name='category-detail',
                ),
            )
        if self.item_slug_field:
            urlpatterns += patterns('',
                url(r'^i/(?P<slug>.+)/$', 
                    self.item_view_class.as_view(document=item_document,
                                            slug_field=self.item_slug_field,
                                            queryset=item_index,
                                            view_point=self,
                                            configuration=self._configuration_from_prefix(params, 'item'),),
                    name='item-detail',
                ),
            )
        else:
            urlpatterns += patterns('',
                url(r'^i/(?P<pk>.+)/$', 
                    self.item_view_class.as_view(document=item_document,
                                            queryset=item_index,
                                            view_point=self,
                                            configuration=self._configuration_from_prefix(params, 'item'),),
                    name='item-detail',
                ),
            )
        return urlpatterns

