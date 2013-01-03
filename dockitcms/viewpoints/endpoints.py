from hyperadmin.endpoints import Endpoint, LinkPrototype
from hyperadmin.apirequests import InternalAPIRequest

from django.conf.urls.defaults import url


class ChainedAPIRequest(InternalAPIRequest):
    def __init__(self, api_request, site, path='/', url_args=[], url_kwargs={}, **kwargs):
        self.outer_api_request = api_request
        url_args = api_request.url_args
        url_kwargs = api_request.url_kwargs
        kwargs.setdefault('payload', api_request.payload)
        kwargs.setdefault('method', api_request.method)
        kwargs.setdefault('params', api_request.params)
        super(ChainedAPIRequest, self).__init__(site, path, url_args, url_kwargs, **kwargs)
        self.session_state.update(api_request.session_state)
    
    def get_full_path(self):
        #TODO
        return self.outer_api_request.get_full_path()
    
    @property
    def user(self):
        return self.outer_api_request.user

class ChainedLinkPrototype(LinkPrototype):
    def __init__(self, outer_endpoint, inner_prototype):
        self.outer_endpoint = outer_endpoint
        self.inner_prototype = inner_prototype
    
    @property
    def name(self):
        return self.inner_prototype.name
    
    @property
    def endpoint(self):
        return self.inner_prototype.endpoint
    
    @property
    def resource(self):
        return self.inner_prototype.resource
    
    @property
    def state(self):
        return self.inner_prototype.state
    
    @property
    def common_state(self):
        return self.inner_prototype.common_state
    
    @property
    def api_request(self):
        return self.inner_prototype.api_request
    
    def show_link(self, **kwargs):
        """
        Checks the state and returns False if the link is not active.
        """
        return self.inner_prototype.show_link(**kwargs)
    
    def get_link(self, **link_kwargs):
        link_kwargs['url'] = self.get_url()
        return self.inner_prototype.get_link(**link_kwargs)
    
    def handle_submission(self, link, submit_kwargs):
        return self.inner_prototype.handle_submission(link, submit_kwargs)
    
    def get_url(self, **kwargs):
        return self.outer_endpoint.get_url(**kwargs)
    
    def get_url_name(self):
        return self.outer_endpoint.get_url_name()

class BaseViewPointEndpoint(Endpoint):
    view_point = None
    configuration = None
    
    def get_internal_api_request_kwargs(self, **kwargs):
        params = {'api_request':self.api_request,
                  'site':self.get_inner_site(),
                  'path':self.api_request.get_full_path(),}
        params.update(kwargs)
        return params
    
    def get_inner_site(self):
        return self._get_inner_endpoint().site
    
    def _get_inner_endpoint(self):
        return self.view_point.get_resource_endpoint()
    
    def get_inner_endpoint(self):
        if self.api_request:
            if not hasattr(self, 'innerl_endpoint'):
                kwargs = self.get_internal_api_request_kwargs()
                self.internal_api_request = ChainedAPIRequest(**kwargs)
                self.inner_endpoint = self._get_inner_endpoint().fork(api_request=self.internal_api_request)
            return self.inner_endpoint
        return self._get_inner_endpoint()
    
    def get_url_name(self):
        return self.get_inner_endpoint().get_url_name()
    
    def get_url_suffix(self):
        return self.get_inner_endpoint().get_url_suffix()
    
    def get_name_suffix(self):
        return self.get_inner_endpoint().get_name_suffix()
    
    def get_url_object(self):
        view = self.get_view()
        return url(self.get_url_suffix(), view, name=self.get_url_name(),)
    
    def get_link_prototypes(self):
        if not hasattr(self, '_link_prototypes'):
            self._link_prototypes = dict()
            for key, proto in self.get_inner_endpoint().get_link_prototypes().iteritems():
                self._link_prototypes[key] = ChainedLinkPrototype(self, proto)
        return self._link_prototypes
    
    def get_resource_items(self):
        #TODO chained resource item
        return self.get_inner_endpoint().get_resource_items()

class ListEndpoint(BaseViewPointEndpoint):
    pass

class DetailEndpoint(BaseViewPointEndpoint):
    pass
