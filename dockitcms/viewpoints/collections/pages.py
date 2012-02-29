from common import CollectionMixin, PointDetailView

from dockitcms.models import BaseViewPoint
from dockitcms.viewpoints.common import CanonicalMixin, TemplateMixin

from dockit import schema

from django.conf.urls.defaults import patterns, url

class URLDetailView(PointDetailView):
    url_field = None
    
    def get_object(self):
        queryset = self.get_queryset()
        url = self.kwargs['url']
        if not url.startswith('/'):
            url = '/' + url
        return queryset.get(**{self.url_field: url})

class PagesViewPoint(BaseViewPoint, CollectionMixin, CanonicalMixin, TemplateMixin):
    '''
    View point whose collection represent pages with their own urls
    '''
    url_field = schema.CharField()
    
    view_class = URLDetailView
    
    def contains_url(self, url):
        return self.get_base_index().filter(**{self.url_field: url}).exists()
    
    def get_document(self):
        document = super(PagesViewPoint, self).get_document()
        view_point = self
        
        def get_absolute_url_for_instance(instance):
            return view_point.reverse('detail', getattr(instance, view_point.url_field))
        
        if self.canonical:
            document.get_absolute_url = get_absolute_url_for_instance
        
        return document
    
    def get_base_index(self):
        index = super(PagesViewPoint, self).get_base_index()
        index = index.index(self.url_field)
        return index
    
    def get_urls(self):
        params = self.to_primitive(self)
        document = self.get_document()
        index = self.get_base_index()
        urlpatterns = patterns('',
            url(r'^(?P<url>.+)$', 
                self.view_class.as_view(document=document,
                                      queryset=index,
                                      view_point=self,
                                      url_field=self.url_field,
                                      configuration=params,),
                name='detail',
            ),
        )
        return urlpatterns
    
    class Meta:
        typed_key = 'dockitcms.collectionpages'

