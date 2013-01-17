"""
Resource classes for powering the public facing API go here. These classes proxy functionality from the collections/virtual API.
"""
from hyperadmin.sites import BaseResourceSite
from hyperadmin.resources import BaseResource
from hyperadmin.resources.directory import ResourceDirectory
from hyperadmin.resources.endpoints import ResourceEndpoint
from hyperadmin.links import LinkPrototype, LinkCollectionProvider
from hyperadmin.states import EndpointState
from hyperadmin.resources.hyperobjects import ResourceItem
from hyperadmin.apirequests import InternalAPIRequest

from django.conf.urls.defaults import patterns, url, include


class ChainedAPIRequest(InternalAPIRequest):
    def __init__(self, api_request, site, state, path='/', url_args=[], url_kwargs={}, **kwargs):
        self.outer_api_request = api_request
        url_args = api_request.url_args
        url_kwargs = api_request.url_kwargs
        self.state = state
        kwargs.setdefault('payload', api_request.payload)
        kwargs.setdefault('method', api_request.method)
        kwargs.setdefault('params', api_request.params)
        super(ChainedAPIRequest, self).__init__(site, path, url_args, url_kwargs, **kwargs)
        self.session_state.update(api_request.session_state)
        self.session_state['site'] = self.outer_api_request.site
    
    def get_full_path(self):
        #TODO
        return self.outer_api_request.get_full_path()
    
    @property
    def user(self):
        return self.outer_api_request.user
    
    def generate_response(self, link, state):
        return self.outer_api_request.generate_response(link, self.state)
    
    @property
    def request(self):
        return self.outer_api_request.request
    
    def get_link_prototypes(self, endpoint):
        urlname = endpoint.get_url_name()
        try:
            outer_endpoint = self.outer_api_request.get_endpoint(urlname)
        except KeyError:
            return {}
        return self.outer_api_request.get_link_prototypes(outer_endpoint)
        

class ChainedLinkPrototype(LinkPrototype):
    def __init__(self, endpoint, outer_api_request, inner_prototype):
        #endpoint is discarded
        self.outer_api_request = outer_api_request
        self.inner_prototype = inner_prototype
        inner_prototype.get_url = self.get_url
    
    @property
    def outer_endpoint(self):
        try:
            return self.outer_api_request.get_endpoint(self.get_url_name())
        except KeyError:
            return self.outer_api_request.get_resource(self.get_url_name())
    
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
        #TODO check if link resolves on outer_endpoint
        return self.inner_prototype.show_link(**kwargs)
    
    def get_link(self, **link_kwargs):
        return self.inner_prototype.get_link(**link_kwargs)
    
    def handle_submission(self, link, submit_kwargs):
        return self.inner_prototype.handle_submission(link, submit_kwargs)
    
    def get_url(self, **kwargs):
        return self.endpoint.get_url(**kwargs)
    
    def get_url_name(self):
        return self.endpoint.get_url_name()

#this is a mouthful
class PublicEndpointStateLinkCollectionProvider(LinkCollectionProvider):
    def _get_link_functions(self, attr):
        functions = super(PublicEndpointStateLinkCollectionProvider, self)._get_link_functions(attr)
        #TODO these inner links need post-processing
        inner_links = getattr(self.container.inner_state.links, attr)
        functions.append(inner_links)
        return functions

class PublicEndpointState(EndpointState):
    #TODO links should consult inner_state, rewrite urls if they exist
    #get_namespaces
    
    link_collector_class = PublicEndpointStateLinkCollectionProvider
    
    @property
    def inner_endpoint(self):
        return self.endpoint.get_inner_endpoint()
    
    @property
    def inner_state(self):
        return self.inner_endpoint.state
    
    def get_item(self):
        if self.inner_state.item:
            return self.endpoint.get_resource_item(self.inner_state.item)
        return None
    item = property(get_item)
    
    def get_resource_items(self):
        instances = self.inner_state.get_resource_items()
        return [self.endpoint.get_resource_item(instance) for instance in instances]

class PublicResourceItem(ResourceItem):
    """
    Where instance is an inner resource item
    """
    @property
    def form(self):
        return self.instance.form
    
    def get_prompt(self):
        return self.instance.get_prompt()
    
    #links
    #get_resource_items
    #get_absolute_url
    #get_namespaces
    #get_link

class PublicMixin(object):
    state_class = PublicEndpointState
    resource_item_class = PublicResourceItem
    inner_endpoint = None
    
    def get_inner_apirequest_kwargs(self, **kwargs):
        params = {'api_request':self.api_request,
                  'site':self.get_inner_site(),
                  'path':self.api_request.get_full_path(),
                  'state':self.state,}
        params.update(kwargs)
        return params
    
    def get_inner_site(self):
        return self.inner_endpoint.site
    
    def get_inner_apirequest(self):
        if not hasattr(self, 'inner_apirequest'):
            if 'inner_apirequest' not in self.api_request.session_state:
                kwargs = self.get_inner_apirequest_kwargs()
                inner_apirequest = ChainedAPIRequest(**kwargs)
                self.api_request.session_state['inner_apirequest'] = inner_apirequest
            self.inner_apirequest = self.api_request.session_state['inner_apirequest']
        return self.inner_apirequest
    
    def get_inner_endpoint(self):
        if self.api_request:
            if not hasattr(self, 'bound_inner_endpoint'):
                inner_apirequest = self.get_inner_apirequest()
                urlname = self.get_url_name()
                self.bound_inner_endpoint = inner_apirequest.get_endpoint(urlname)
            return self.bound_inner_endpoint
        return self.inner_endpoint
    
    #def get_url_name(self):
    #    return self.inner_endpoint.get_url_name()
    
    def get_url_suffix(self):
        ending = self.inner_endpoint.get_url_suffix()
        if ending.startswith('^'):
            ending = ending[1:]
        if self.url_suffix:
            return self.url_suffix + ending
        return ending
    
    def get_name_suffix(self):
        return self.inner_endpoint.get_name_suffix()
    
    def get_link_prototypes(self):
        prototypes = list()
        inner_link_prototypes = self.get_inner_endpoint().create_link_prototypes()
        for key, proto in inner_link_prototypes.iteritems():
            prototypes.append((ChainedLinkPrototype, {'inner_prototype':proto, 'outer_api_request':self.api_request}))
        return prototypes
    
    def get_instances(self):
        return self.get_inner_endpoint().get_resource_items()
    
    def get_resource_item(self, instance, **kwargs):
        kwargs.setdefault('endpoint', self)
        return self.get_resource_item_class()(instance=instance, **kwargs)
    
    def get_resource_items(self):
        instances = self.get_instances()
        return [self.get_resource_item(instance) for instance in instances]

class PublicResourceDirectory(ResourceDirectory):
    def get_urls(self):
        urlpatterns = super(ResourceDirectory, self).get_urls()
        for key, resource in self.resource_adaptor.iteritems():
            urlpatterns += patterns('',
                url(resource.base_url, include(resource.urls))
            )
        return urlpatterns

class PublicSubsite(BaseResourceSite):
    """
    The public facing API that exposes functionality from the VirtualResourceSite/Collections API
    
    What kind of resource?
    """
    directory_resource_class = PublicResourceDirectory
    name = 'cmssite'
    subsite = None
    api_endpoint = None
    
    def post_register(self):
        super(PublicSubsite, self).post_register()
        self.register_builtin_media_types()

class PublicResource(PublicMixin, BaseResource):
    app_name = None
    collection = None
    view_points = None
    base_url = None
    
    def post_register(self):
        self.api_resource = self.collection.get_collection_resource()
        super(PublicResource, self).post_register()
    
    @property
    def inner_endpoint(self):
        return self.api_resource
    
    def get_parent(self):
        return self._parent
    
    def set_parent(self, parent):
        self._parent = parent
    
    parent = property(get_parent, set_parent)
    
    def get_resource_name(self):
        return self.collection.title
    resource_name = property(get_resource_name)
    
    def get_view_endpoints(self):
        endpoints = list()
        for view_point in self.view_points:
            endpoints.extend(view_point.get_view_endpoints())
        return endpoints
    
    def get_breadcrumbs(self):
        breadcrumbs = self.create_link_collection()
        #resources & apps don't have breadcrumbs do they?
        #breadcrumbs.append(self.get_breadcrumb())
        return breadcrumbs
    
    def get_prompt(self):
        return self.api_resource.get_prompt()
    
    def get_url_name(self):
        return self.api_resource.get_url_name()
    
    def get_inner_endpoint(self):
        if self.api_request:
            if not hasattr(self, 'bound_inner_endpoint'):
                inner_apirequest = self.get_inner_apirequest()
                urlname = self.get_url_name()
                self.bound_inner_endpoint = inner_apirequest.get_endpoint(urlname)
                #how does this happen?!?
                assert hasattr(self.bound_inner_endpoint, 'endpoints')
            return self.bound_inner_endpoint
        return self.inner_endpoint
    
    def get_item_url(self, item):
        return self.link_prototypes['detail'].get_url(item=item.instance)

class PublicEndpoint(PublicMixin, ResourceEndpoint):
    view_point = None
    
    def get_inner_site(self):
        return self._parent.get_inner_site()
    
    def get_inner_resource(self):
        return self._parent.get_inner_endpoint()
    
    @property
    def inner_endpoint(self):
        endpoint_name = self.view_point.get_endpoint_name()
        return self.get_inner_resource().endpoints[endpoint_name]
    
    def handle_link_submission(self, api_request):
        inner_endpoint = self.get_inner_endpoint()
        inner_endpoint.generate_response = self.generate_response
        ilp = inner_endpoint.link_prototypes
        olp = self.link_prototypes
        return inner_endpoint.dispatch_api(self.get_inner_apirequest())
    
    def get_common_state(self):
        return {}
    common_state = property(get_common_state)
