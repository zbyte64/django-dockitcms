from django.conf.urls.defaults import url, patterns, include

from dockitcms.viewpoints.endpoints import DetailEndpoint
from dockitcms.models import ViewPoint


class PageDetailEndpoint(DetailEndpoint):
    def get_url_object(self):
        #return tuple(self.get_urls())
        return url('', include(self.get_urls()))

    def get_urls(self):
        view = self.get_view()
        urls = list()
        pages = self.resource.resource_adaptor.objects.all()
        original_name = self.get_url_name()
        #produce a url for each page in page_resource
        for page in pages:
            name = page.url_name or original_name
            if page.path is None: #TODO is this suppose to happen as part of admin save
                page.path = page.clean_path()
                page.save()
            exp = r'(?P<path>{path})'.format(path=page.path)
            url_part = url(exp, view, name=name)
            urls.append(url_part)
        #return urls
        return patterns('', *urls)

    '''
    def get_urls(self):
        urlpatterns = self.get_extra_urls()
        urls = [endpoint.get_url_object() for endpoint in self.get_children_endpoints()]
        urlpatterns += patterns('', *urls)
        return urlpatterns
    '''

class PageViewPoint(ViewPoint):
    page_resource = None
    view_endpoint_class = PageDetailEndpoint

    def get_endpoint_name(self):
        return 'detail'

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
