from dockitcms.models import ViewPoint
from dockitcms.viewpoints.common import AuthenticatedMixin, CanonicalMixin, TEMPLATE_SOURCE_CHOICES
from common import CollectionMixin, PointListView, PointDetailView

from dockit import schema
from dockit.forms import DocumentForm

from django.conf.urls.defaults import patterns, url
from django import forms
from django.template import Template, TemplateSyntaxError
from django.utils.translation import ugettext_lazy as _

class CollectionListingViewPoint(CanonicalMixin, CollectionMixin, AuthenticatedMixin, ViewPoint):
    view_type = ViewPoint._meta.fields['view_type'] #hack around
    slug_field = schema.SlugField(blank=True)
    list_template_source = schema.CharField(choices=TEMPLATE_SOURCE_CHOICES, default='name')
    list_template_name = schema.CharField(default='dockitcms/list.html', blank=True)
    list_template_html = schema.TextField(blank=True)
    list_content = schema.TextField(blank=True)
    detail_template_source = schema.CharField(choices=TEMPLATE_SOURCE_CHOICES, default='name')
    detail_template_name = schema.CharField(default='dockitcms/detail.html', blank=True)
    detail_template_html = schema.TextField(blank=True)
    detail_content = schema.TextField(blank=True)
    paginate_by = schema.IntegerField(blank=True, null=True)
    
    list_view_class = PointListView
    detail_view_class = PointDetailView
    
    def get_base_index(self):
        index = super(CollectionListingViewPoint, self).get_base_index()
        if self.slug_field:
            index = index.index(self.slug_field)
        return index
    
    def register_view_point(self):
        index = self.get_base_index()
        index.commit()
    
    def get_document(self):
        doc_cls = self.collection.get_document()
        view_point = self
        
        def get_absolute_url_for_instance(instance):
            if view_point.slug_field:
                return view_point.reverse('detail', instance[view_point.slug_field])
            return view_point.reverse('detail', instance.pk)
        
        if self.canonical:
            #TODO this does not work
            setattr(doc_cls, 'get_absolute_url', get_absolute_url_for_instance)
            assert hasattr(doc_cls, 'get_absolute_url')
        
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
        document = self.get_document()
        params = self.to_primitive(self)
        index = self.get_base_index()
        urlpatterns = patterns('',
            url(r'^$', 
                self.list_view_class.as_view(document=document,
                                      queryset=index,
                                      view_point=self,
                                      configuration=self._configuration_from_prefix(params, 'list'),
                                      paginate_by=params.get('paginate_by', None)),
                name='index',
            ),
        )
        if params.get('slug_field', None):
            urlpatterns += patterns('',
                url(r'^(?P<slug>.+)/$', 
                    self.detail_view_class.as_view(document=document,
                                            queryset=index,
                                            slug_field=params['slug_field'],
                                            view_point=self,
                                            configuration=self._configuration_from_prefix(params, 'detail'),),
                    name='detail',
                ),
            )
        else:
            urlpatterns += patterns('',
                url(r'^(?P<pk>.+)/$', 
                    self.detail_view_class.as_view(document=document,
                                            queryset=index,
                                            view_point=self,
                                            configuration=self._configuration_from_prefix(params, 'detail'),),
                    name='detail',
                ),
            )
        return urlpatterns
    
    class Meta:
        typed_field = 'view_type'
        collection = ViewPoint._meta.collection
        typed_key = 'dockitcms.collectionlisting'
    
    @classmethod
    def get_admin_form_class(cls):
        return CollectionListingViewPointForm

class CollectionListingViewPointForm(DocumentForm):
    class Meta:
        document = CollectionListingViewPoint
    
    def _clean_template_html(self, content):
        if not content:
            return content
        try:
            Template(content)
        except TemplateSyntaxError, e:
            raise forms.ValidationError(unicode(e))
        return content
    
    def clean_list_template_html(self):
        return self._clean_template_html(self.cleaned_data.get('list_template_html'))
    
    def clean_detail_template_html(self):
        return self._clean_template_html(self.cleaned_data.get('detail_template_html'))
    
    def clean_list_content(self):
        return self._clean_template_html(self.cleaned_data.get('list_content'))
    
    def clean_detail_content(self):
        return self._clean_template_html(self.cleaned_data.get('detail_content'))
    
    def clean(self):
        #TODO pump the error to their perspective field
        if self.cleaned_data.get('list_template_source') == 'name':
            if not self.cleaned_data.get('list_template_name'):
                raise forms.ValidationError(_('Please specify a list template name'))
        if self.cleaned_data.get('list_template_source') == 'html':
            if not self.cleaned_data.get('list_template_html'):
                raise forms.ValidationError(_('Please specify the list template html'))
        
        if self.cleaned_data.get('detail_template_source') == 'name':
            if not self.cleaned_data.get('detail_template_name'):
                raise forms.ValidationError(_('Please specify a detail template name'))
        if self.cleaned_data.get('detail_template_source') == 'html':
            if not self.cleaned_data.get('detail_template_html'):
                raise forms.ValidationError(_('Please specify the detail template html'))
        return self.cleaned_data

