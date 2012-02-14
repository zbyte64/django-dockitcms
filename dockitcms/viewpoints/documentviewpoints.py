from forms import TemplateFormMixin

from dockitcms.utils import ConfigurableTemplateResponseMixin
from dockitcms.models import ViewPoint, Collection

import dockit
from dockit.forms import DocumentForm
from dockit.views import ListView, DetailView

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

class BaseCollectionViewPoint(ViewPoint):
    collection = dockit.ReferenceField(Collection)
    template_source = dockit.CharField(choices=TEMPLATE_SOURCE_CHOICES, default='name')
    template_name = dockit.CharField(default='dockitcms/list.html', blank=True)
    template_html = dockit.TextField(blank=True)
    content = dockit.TextField(blank=True)
    #TODO filters
    
    view_class = None
    
    class Meta:
        proxy = True
    
    @classmethod
    def get_admin_form_class(cls):
        return BaseCollectionViewPointForm
    
    def get_document(self):
        return self.collection.get_document()

class CollectionListViewPoint(BaseCollectionViewPoint):
    paginate_by = dockit.IntegerField(blank=True, null=True)
    #TODO order by
    
    view_class = PointListView
    
    def get_urls(self):
        params = self.to_primitive(self)
        document = self.get_document()
        urlpatterns = patterns('',
            url(r'^$', 
                self.view_class.as_view(document=document,
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
    
    def register_view_point(self):
        if self.slug_field:
            doc_cls = self.collection.get_document()
            doc_cls.objects.index(self.slug_field).commit()
    
    def get_urls(self):
        params = self.to_primitive(self)
        document = self.get_document()
        if self.slug_field:
            return patterns('',
                url(r'^(?P<slug>.+)/$',
                    self.view_class.as_view(document=document,
                                          configuration=params,
                                          slug_field=self.slug_field,),
                    name='index',
                ),
            )
        else:
            return patterns('',
                url(r'^(?P<pk>.+)/$',
                    self.view_class.as_view(document=document,
                                          configuration=params,),
                    name='index',
                ),
            )
    
    class Meta:
        typed_key = 'dockitcms.collectiondetailview'

class BaseCollectionViewPointForm(TemplateFormMixin, DocumentForm):
    class Meta:
        document = BaseCollectionViewPoint

