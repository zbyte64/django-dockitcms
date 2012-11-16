from dockitcms.viewpoints.forms import TemplateFormMixin
from dockitcms.viewpoints.common import TemplateMixin, ResourceEndpointMixin, PointListView, PointDetailView, LIST_CONTEXT_DESCRIPTION, DETAIL_CONTEXT_DESCRIPTION

from dockitcms.models import ViewPoint

from dockit import schema
from dockit.forms import DocumentForm

from django.utils.translation import ugettext_lazy as _
from django import forms

#TODO IndexMixin => SingleResourceMixin/ResourceEndpointMixin; CONSIDER: what about index lookups, should factor down to seperate endpoints for each index
class BaseViewPoint(ViewPoint, ResourceEndpointMixin, TemplateMixin):
    view_class = None
    view_endpoint_class = None #TODO
    
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
                }
        }
        params.update(kwargs)
        return params
    
    def register_view_endpoints(self, site):
        #we assume that the resource adaptor is the same object in both the Collections API and the Public API
        resource = site.get_resource(self.resource.resource_adaptor)
        klass = self.get_view_endpoint_class()
        kwargs = self.get_view_endpoint_kwargs(resource=resource)
        endpoint = klass(**kwargs)
        resource.register_endpoint(endpoint) #TODO support this method
    
    def get_view_endpoint_options(self):
        return {'view_point':self,
                'configuration':{
                    'template_source':self.template_source,
                    'template_name':self.template_name,
                    'template_html':self.template_html,
                    'content':self.content,
                }
        }
    
    def get_view_endpoint_definitions(self):
        return [{
            'url':self.get_url_regexp(),
            'view_class':self.view_class,
            'resource': self.resource, #TODO migrate from index
            'endpoint_name': self.endpoint_name, #TODO populated from selecting an endpoint
            'url_name': self.url_name or self.endpoint_name, #TODO
            'options':self.get_view_endpoint_options(),
        }]

class ListViewPoint(BaseViewPoint, TemplateMixin):
    paginate_by = schema.IntegerField(blank=True, null=True)
    #order_by = schema.CharField(blank=True)
    
    view_class = PointListView
    
    #def get_view_endpoint_options(self):
    #    return {}
    #    #TODO
    #    return {'paginate_by':self.paginate_by}
    
    class Meta:
        typed_key = 'dockitcms.listview'
    
    @classmethod
    def get_admin_form_class(cls):
        return ListViewPointForm

class DetailViewPoint(BaseViewPoint, TemplateMixin):
    slug_field = schema.SlugField(blank=True)
    
    view_class = PointDetailView
    
    def get_url(self):
        url = super(DetailViewPoint, self).get_url()
        if self.slug_field:
            url += '(?P<slug>\w\d\-+)/$'
        else:
            url += str(self.get_resource_endpoint()['url'])[1:]
        return url
    
    def get_object_class(self):
        object_class = super(DetailViewPoint, self).get_object_class()
        return object_class
        #TODO
        view_point = self
        
        def get_absolute_url_for_instance(instance):
            if view_point.slug_field:
                return view_point.reverse('detail', instance[view_point.slug_field])
            return view_point.reverse('detail', instance.pk)
        
        if self.canonical:
            object_class.get_absolute_url = get_absolute_url_for_instance
        
        return object_class
    
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

