from dockitcms.resources.public import PublicEndpoint

from django.template.response import TemplateResponse


class BaseViewPointEndpoint(PublicEndpoint):
    configuration = None
    
    def get_template_names(self):
        return self.view_point.get_template_names()
    
    def get_context_data(self, **kwargs):
        kwargs.setdefault('resource_items', kwargs['state'].get_resource_items())
        kwargs = super(BaseViewPointEndpoint, self).get_context_data(**kwargs)
        kwargs['content'] = self.view_point.render_content(kwargs)
        return kwargs

class ListEndpoint(BaseViewPointEndpoint):
    def get_context_data(self, **kwargs):
        kwargs['object_list'] = [item.instance.instance for item in kwargs['state'].get_resource_items()]
        return super(ListEndpoint, self).get_context_data(**kwargs)

class DetailEndpoint(BaseViewPointEndpoint):
    def get_context_data(self, **kwargs):
        kwargs['object'] = kwargs['state'].get_resource_items()[0].instance.instance
        return super(DetailEndpoint, self).get_context_data(**kwargs)
