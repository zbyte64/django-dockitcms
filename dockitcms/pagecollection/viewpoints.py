from dockitcms.viewpoints.endpoints import DetailEndpoint
from dockitcms.models import ViewPoint


class PageViewPoint(ViewPoint):
    page_resource = None
    view_endpoint_class = DetailEndpoint

    def get_urls(self):
        #TODO produce a url for each page in page_resource
        return super(PageViewPoint, self).get_urls()

    def get_endpoint_name(self):
        return 'list'

    def render_content(self, kwargs={}):
        return ''

    def get_view_endpoint_class(self):
        return self.view_endpoint_class

    def get_view_endpoint_kwargs(self, **kwargs):
        params = {'view_point':self,}
        params.update(kwargs)
        return params

    def get_view_endpoints(self):
        klass = self.get_view_endpoint_class()
        kwargs = self.get_view_endpoint_kwargs()
        return [(klass, kwargs)]

    #def get_template_names(self):
    #    instance = self.state.item
    #    if instance.template:
    #        return instance._page_def.get_template(instance.template)

    class Meta:
        proxy = True
