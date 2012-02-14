from dockitcms.utils import ConfigurableTemplateResponseMixin
from dockitcms.models import ViewPoint, Collection
from dockitcms.viewpoints.forms import TemplateFormMixin

import dockit
from dockit.forms import DocumentForm
from dockit.views import ListView

from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext_lazy as _

from models import DocumentCategoryModel

TEMPLATE_SOURCE_CHOICES = [
    ('name', _('By Template Name')),
    ('html', _('By Template HTML')),
]

CONTEXT_DESCRIPTION = '''
The following context is provided:<br/>
category: the category matching the url path<br/>
object_list: the items belonging to the category</br/>
paginator: the paginator object<br/>
'''

class CategoryDetailView(ConfigurableTemplateResponseMixin, ListView):
    document = None
    category_queryset = DocumentCategoryModel.objects.listed()
    category_document = None

    def get_queryset(self):
        return self.document.objects.filter.view_category(self.category.pk)
    
    def get_category(self):
        category_index = self.category_queryset.get(path=self.kwargs['path'],
                                                    collection=self.category_document._meta.collection)
        return self.category_document.objects.get(category_index.document_id)
    
    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        context['category'] = self.category
        return context
    
    def get(self, request, *args, **kwargs):
        self.category = self.get_category()
        return super(CategoryDetailView, self).get(request, *args, **kwargs)

class CategoryViewPoint(ViewPoint):
    category_collection = dockit.ReferenceField(Collection)
    
    item_collection = dockit.ReferenceField(Collection)
    item_category_dot_path = dockit.CharField()
    
    paginate_by = dockit.IntegerField(blank=True, null=True)
    
    template_source = dockit.CharField(choices=TEMPLATE_SOURCE_CHOICES, default='name')
    template_name = dockit.CharField(default='dockitcms/list.html', blank=True)
    template_html = dockit.TextField(blank=True)
    content = dockit.TextField(blank=True, help_text=CONTEXT_DESCRIPTION)
    #TODO filters
    
    view_class = CategoryDetailView
    
    def register_view_point(self):
        if self.item_category_dot_path:
            doc_cls = self.item_collection.get_document()
            doc_cls.objects.index(self.item_category_dot_path).commit()
    
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
        return self.item_collection.get_document()
    
    @classmethod
    def get_admin_form_class(cls):
        return CategoryViewPointForm
    
    def get_urls(self):
        category_document = self.get_category_document()
        item_document = self.get_item_document()
        params = self.to_primitive(self)
        
        url_pattern = r'^(?P<path>.+)/$'
        if 'path' in self.url_regexp.groupindex:
            url_pattern = r'^'
        
        urlpatterns = patterns('',
            url(url_pattern,
                self.view_class.as_view(document=item_document,
                                        category_document=category_document,
                                        paginate_by=self.paginate_by,
                                        configuration=params,),
                name='category-detail',
            ),
        )
        return urlpatterns
    
    class Meta:
        typed_key = 'contrib.dagcategory'

class CategoryViewPointForm(TemplateFormMixin, DocumentForm):
    class Meta:
        document = CategoryViewPoint

