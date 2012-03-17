from .forms import TemplateFormMixin
from .common import CanonicalMixin, TemplateMixin, IndexMixin, PointListView, PointDetailView, LIST_CONTEXT_DESCRIPTION, DETAIL_CONTEXT_DESCRIPTION

from dockitcms.models import ViewPoint

from dockit import schema
from dockit.forms import DocumentForm

from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django import forms

class BaseViewPoint(ViewPoint, IndexMixin, TemplateMixin):
    view_class = None
    
    class Meta:
        proxy = True
    
    @classmethod
    def get_admin_form_class(cls):
        return BaseViewPointForm

class ListViewPoint(BaseViewPoint, TemplateMixin):
    paginate_by = schema.IntegerField(blank=True, null=True)
    #order_by = schema.CharField(blank=True)
    
    view_class = PointListView
    
    def get_urls(self):
        params = self.to_primitive(self)
        object_class = self.get_object_class()
        index = self.get_index()
        urlpatterns = patterns('',
            url(r'^$', 
                self.view_class.as_view(document=object_class,
                                      queryset=index,
                                      view_point=self,
                                      configuration=params,
                                      paginate_by=self.paginate_by),
                                      #order_by=self.order_by),
                name='index',
            ),
        )
        return urlpatterns
    
    class Meta:
        typed_key = 'dockitcms.listview'
    
    @classmethod
    def get_admin_form_class(cls):
        return ListViewPointForm

class DetailViewPoint(BaseViewPoint, TemplateMixin, CanonicalMixin):
    slug_field = schema.SlugField(blank=True)
    
    view_class = PointDetailView
    
    def get_object_class(self):
        object_class = super(DetailViewPoint, self).get_object_class()
        view_point = self
        
        def get_absolute_url_for_instance(instance):
            if view_point.slug_field:
                return view_point.reverse('detail', instance[view_point.slug_field])
            return view_point.reverse('detail', instance.pk)
        
        if self.canonical:
            object_class.get_absolute_url = get_absolute_url_for_instance
        
        return object_class
    
    def get_urls(self):
        params = self.to_primitive(self)
        object_class = self.get_object_class()
        index = self.get_index()
        if self.slug_field:
            return patterns('',
                url(r'^(?P<slug>.+)/$',
                    self.view_class.as_view(document=object_class,
                                          queryset=index,
                                          view_point=self,
                                          configuration=params,
                                          slug_field=self.slug_field,),
                    name='index',
                ),
            )
        else:
            return patterns('',
                url(r'^(?P<pk>.+)/$',
                    self.view_class.as_view(document=object_class,
                                          queryset=index,
                                          view_point=self,
                                          configuration=params,),
                    name='index',
                ),
            )
    
    class Meta:
        typed_key = 'dockitcms.detailview'
    
    @classmethod
    def get_admin_form_class(cls):
        return DetailViewPointForm

class BaseViewPointForm(TemplateFormMixin, DocumentForm):
    class Meta:
        document = BaseViewPoint

class ListViewPointForm(BaseViewPointForm):
    template_name = forms.CharField(initial='dockitcms/list.html', required=False)
    content = forms.CharField(help_text=LIST_CONTEXT_DESCRIPTION, required=False, widget=forms.Textarea)

class DetailViewPointForm(BaseViewPointForm):
    template_name = forms.CharField(initial='dockitcms/detail.html', required=False)
    content = forms.CharField(help_text=DETAIL_CONTEXT_DESCRIPTION, required=False, widget=forms.Textarea)

