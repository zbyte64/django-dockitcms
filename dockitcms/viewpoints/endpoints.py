from hyperadmin.endpoints import Endpoint

from django.conf.urls.defaults import url


class BaseViewPointEndpoint(Endpoint):
    view_point = None
    configuration = None
    
    #def __init__(self, resource, view_point, configuration):
    #    self.view_point = view_point
    #    self.configuration = configuration
    #    super(BaseViewPointEndpoint, self).__init__(resource=resource)
    
    def get_original_endpoint(self):
        return self.view_point.get_resource_endpoint()
    '''
    def get_view_kwargs(self):
        kwargs = self.resource.get_view_kwargs()
        kwargs['endpoint'] = self
        return kwargs
    
    def get_view_class(self):
        return self.get_original_endpoint().get_view_class()
        return self.view_class
    
    def get_view(self):
        init = self.get_view_kwargs()
        klass = self.get_view_class()
        assert klass
        return klass.as_view(**init)
    '''
    def get_url_name(self):
        base_name = self.resource.get_base_url_name()
        return base_name + self.get_original_endpoint().name_suffix
    
    def get_url_suffix(self):
        return self.get_original_endpoint().get_url_suffix()
    
    def get_url_object(self):
        view = self.get_view()
        return url(self.get_url_suffix(), view, name=self.get_url_name(),)
    '''
    def get_url_object(self):
        return url(self.get_url_suffix(), self.get_view(), name=self.get_url_name(),)
    
    def get_url(self, **kwargs):
        return self.resource.reverse(self.get_url_name(), **kwargs)
    '''
    #TODO better name => get_internal_links?
    def get_links(self):
        """
        return a dictionary of endpoint links
        """
        return {}

class ListEndpoint(BaseViewPointEndpoint):
    pass

class DetailEndpoint(BaseViewPointEndpoint):
    pass
