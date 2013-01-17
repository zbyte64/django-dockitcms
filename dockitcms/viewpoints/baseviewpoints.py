from dockitcms.viewpoints.forms import TemplateFormMixin
from dockitcms.viewpoints.common import TemplateMixin, LIST_CONTEXT_DESCRIPTION, DETAIL_CONTEXT_DESCRIPTION
from dockitcms.viewpoints.endpoints import ListEndpoint, DetailEndpoint

from dockitcms.models import ViewPoint

from dockit import schema
from dockit.forms import DocumentForm

from django.utils.translation import ugettext_lazy as _
from django import forms


class BaseViewPoint(ViewPoint, TemplateMixin):
    view_class = None
    view_endpoint_class = None
    
    class Meta:
        proxy = True
    
    @classmethod
    def get_admin_form_class(cls):
        return BaseViewPointForm
    
    def get_view_endpoint_class(self):
        return self.view_endpoint_class
    
    def get_view_endpoint_kwargs(self, **kwargs):
        params = {'view_point':self,
                  'configuration':{
                    'template_source':self.template_source,
                    'template_name':self.template_name,
                    'template_html':self.template_html,
                    'content':self.content,
                 },
        }
        params.update(kwargs)
        return super(BaseViewPoint, self).get_view_endpoint_kwargs(**params)
    
    def get_view_endpoints(self):
        klass = self.get_view_endpoint_class()
        kwargs = self.get_view_endpoint_kwargs()
        return [(klass, kwargs)]

class ListViewPoint(BaseViewPoint, TemplateMixin):
    paginate_by = schema.IntegerField(blank=True, null=True)
    #order_by = schema.CharField(blank=True)
    
    default_endpoint_name = 'list'
    
    view_endpoint_class = ListEndpoint
    
    class Meta:
        typed_key = 'dockitcms.listview'
    
    @classmethod
    def get_admin_form_class(cls):
        return ListViewPointForm

class DetailViewPoint(BaseViewPoint, TemplateMixin):
    default_endpoint_name = 'detail'
    
    view_endpoint_class = DetailEndpoint
    
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

