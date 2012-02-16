from dockitcms.viewpoints.forms import TemplateFormMixin

from dockitcms.utils import ConfigurableTemplateResponseMixin
from dockitcms.models import ViewPoint

import dockit
from dockit.forms import DocumentForm

from django.views.generic import ListView, DetailView
from django.conf.urls.defaults import patterns, url
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
                                      paginate_by=self.paginate_by),
                name='index',
            ),
        )
        return urlpatterns
    
    class Meta:
        typed_key = 'dockitcms.modellistview'

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
        typed_key = 'dockitcms.modeldetailview'

class BaseModelViewPointForm(TemplateFormMixin, DocumentForm):
    class Meta:
        document = BaseModelViewPoint

