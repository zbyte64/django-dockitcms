from dockitcms.utils import ConfigurableTemplateResponseMixin, generate_object_detail_scaffold, generate_object_list_scaffold
from dockitcms.models import ViewPoint

import dockit
from dockit.forms import DocumentForm

from django.views.generic import ListView, DetailView
from django.conf.urls.defaults import patterns, url
from django import forms
from django.template import Template, TemplateSyntaxError
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType


TEMPLATE_SOURCE_CHOICES = [
    ('name', _('By Template Name')),
    ('html', _('By Template HTML')),
]

class PointListView(ConfigurableTemplateResponseMixin, ListView):
    pass

class PointDetailView(ConfigurableTemplateResponseMixin, DetailView):
    pass

class BaseModelViewPoint(ViewPoint):
    model = dockit.ModelReferenceField(ContentType)
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
        return BaseModelViewPointForm

class ModelListViewPoint(BaseModelViewPoint):
    paginate_by = dockit.IntegerField(blank=True, null=True)
    #TODO order by
    
    view_class = PointListView
    
    def get_urls(self):
        params = self.to_primitive(self)
        urlpatterns = patterns('',
            url(r'^$', 
                self.view_class.as_view(model=self.model.model_class(),
                                      configuration=params,
                                      paginate_by=params.get('paginate_by', None)),
                name='index',
            ),
        )
        return urlpatterns
    
    class Meta:
        typed_key = 'modellistview'

class ModelDetailViewPoint(BaseModelViewPoint):
    slug_field = dockit.SlugField(blank=True)
    
    view_class = PointDetailView
    
    def get_urls(self):
        params = self.to_primitive(self)
        if self.slug_field:
            return patterns('',
                url(r'^(?P<slug>.+)/$',
                    self.view_class.as_view(model=self.model.model_class(),
                                          configuration=params,
                                          slug_field=self.slug_field,),
                    name='index',
                ),
            )
        else:
            return patterns('',
                url(r'^(?P<pk>.+)/$',
                    self.view_class.as_view(model=self.model.model_class(),
                                          configuration=params,),
                    name='index',
                ),
            )
    
    class Meta:
        typed_key = 'modeldetailview'

class BaseModelViewPointForm(DocumentForm):
    class Meta:
        document = BaseModelViewPoint
    
    def _clean_template_html(self, content):
        if not content:
            return content
        try:
            Template(content)
        except TemplateSyntaxError, e:
            raise forms.ValidationError(unicode(e))
        return content
    
    def clean_template_html(self):
        return self._clean_template_html(self.cleaned_data.get('template_html'))
    
    def clean_content(self):
        return self._clean_template_html(self.cleaned_data.get('content'))
    
    def clean(self):
        #TODO pump the error to their perspective field
        if self.cleaned_data.get('template_source') == 'name':
            if not self.cleaned_data.get('template_name'):
                raise forms.ValidationError(_('Please specify a template name'))
        if self.cleaned_data.get('template_source') == 'html':
            if not self.cleaned_data.get('template_html'):
                raise forms.ValidationError(_('Please specify the template html'))
        return self.cleaned_data

