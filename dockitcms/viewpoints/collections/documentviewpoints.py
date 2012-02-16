from dockitcms.viewpoints.forms import TemplateFormMixin
from dockitcms.viewpoints.common import AuthenticatedMixin, TemplateMixin

from common import CollectionMixin, PointListView, PointDetailView

from dockitcms.models import ViewPoint

import dockit
from dockit.forms import DocumentForm

from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext_lazy as _

class BaseCollectionViewPoint(CollectionMixin, TemplateMixin, AuthenticatedMixin, ViewPoint):
    view_type = ViewPoint._meta.fields['view_type'] #hack around
    view_class = None
    
    class Meta:
        typed_field = 'view_type'
        collection = ViewPoint._meta.collection
        proxy = True
    
    @classmethod
    def get_admin_form_class(cls):
        return BaseCollectionViewPointForm
    
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

