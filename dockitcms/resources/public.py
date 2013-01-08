"""
Resource classes for powering the public facing API go here. These classes proxy functionality from the collections/virtual API.
"""
from hyperadmin.sites import ResourceSite
from hyperadmin.resources.resources import BaseResource
from hyperadmin.endpoints import Endpoint, LinkPrototype
from hyperadmin.states import EndpointState
from hyperadmin.hyperobjects import ResourceItem, LinkCollectionProvider
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
            try:
                outer_endpoint = self.outer_api_request.get_resource(urlname)
            except KeyError:
                #endpoint does not exist in the public
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
    
    def get_url_name(self):
        return self.inner_endpoint.get_url_name()
    
    def get_url_suffix(self):
        ending = self.inner_endpoint.get_url_suffix()
        if ending.startswith('^'):
            ending = ending[1:]
        return self.url_suffix + ending
    
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

class PublicApplicationResource(BaseResource):
    app_name = None
    
    def __init__(self, **kwargs):
        kwargs.setdefault('resource_adaptor', dict())
        super(PublicApplicationResource, self).__init__(**kwargs)
    
    def register_resource(self, resource):
        key = resource.get_resource_name()
        self.resource_adaptor[key] = resource
    
    def get_urls(self):
        urlpatterns = super(PublicApplicationResource, self).get_urls()
        for key, resource in self.resource_adaptor.iteritems():
            urlpatterns += patterns('',
                url(r'', include(resource.urls))
            )
        return urlpatterns

class PublicSiteResource(BaseResource):
    resource_class = 'resourcelisting'
    
    def __init__(self, **kwargs):
        kwargs.setdefault('resource_adaptor', dict())
        super(PublicSiteResource, self).__init__(**kwargs)
    
    def get_prompt(self):
        return self._site.name
    
    def get_app_name(self):
        return self._site.name
    app_name = property(get_app_name)
    
    def get_urls(self):
        urlpatterns = super(PublicSiteResource, self).get_urls()
        for key, res in self.resources.items():
            urlpatterns += patterns('',
                url(r'', include(res.urls))
            )
        return urlpatterns
    
    @property
    def resources(self):
        return self.site.registry

class PublicSubsite(ResourceSite):
    """
    The public facing API that exposes functionality from the VirtualResourceSite/Collections API
    
    What kind of resource?
    """
    name = 'cmssite'
    application_resource_class = PublicApplicationResource
    site_resource_class = PublicSiteResource
    api_endpoint = None
    
    def __init__(self, **kwargs):
        super(PublicSubsite, self).__init__(**kwargs)
        #TODO media type handler that pumps to the endpoint
        self.register_builtin_media_types()
        
        self.collection_viewpoints = dict()
    
    def post_resource_registration(self, resource):
        return #No app objects in this API yet...
    
    def register_viewpoint(self, view_point):
        for collection, defs in view_point.get_view_endpoints():
            self.collection_viewpoints.setdefault(collection.pk, list())
            self.collection_viewpoints[collection.pk].append(defs)
    
    def register_collection(self, collection):
        collection.register_public_resource(site=self)
    
    def get_public_view_endpoints_for_collection(self, collection):
        return self.collection_viewpoints.get(collection.pk, [])
    
    def fork(self, **kwargs):
        ret = super(PublicSubsite, self).fork(**kwargs)
        ret.collection_viewpoints = self.collection_viewpoints
        return ret

class PublicResource(PublicMixin, BaseResource):
    app_name = None
    collection = None
    
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
    
    def get_view_endpoints(self):
        endpoints = self.site.get_public_view_endpoints_for_collection(self.collection)
        endpoints.extend(self.collection.get_view_endpoints())
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
                self.bound_inner_endpoint = inner_apirequest.get_resource(urlname)
            return self.bound_inner_endpoint
        return self.inner_endpoint
    
    def get_item_url(self, item):
        return self.link_prototypes['update'].get_url(item=item.instance)

class PublicEndpoint(PublicMixin, Endpoint):
    view_point = None
    
    @property
    def inner_endpoint(self):
        return self.view_point.get_resource_endpoint()
    
    def handle_link_submission(self, api_request):
        inner_endpoint = self.get_inner_endpoint()
        inner_endpoint.generate_response = self.generate_response
        ilp = inner_endpoint.link_prototypes
        olp = self.link_prototypes
        return inner_endpoint.dispatch_api(self.get_inner_apirequest())
    
    def get_common_state(self):
        return {}
    common_state = property(get_common_state)
