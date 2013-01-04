"""
Resource classes for powering the public facing API go here. These classes proxy functionality from the collections/virtual API.
"""
from hyperadmin.sites import ResourceSite
from hyperadmin.resources.resources import BaseResource
from hyperadmin.endpoints import Endpoint, LinkPrototype
from hyperadmin.states import EndpointState
from hyperadmin.hyperobjects import ResourceItem
from hyperadmin.apirequests import InternalAPIRequest

from django.conf.urls.defaults import patterns, url, include


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
        #TODO check if link resolves on outer_endpoint
        return self.inner_prototype.show_link(**kwargs)
    
    def get_link(self, **link_kwargs):
        #link_kwargs['url'] = self.get_url()
        #link_kwargs = self.inner_prototype.endpoint.get_link_kwargs(**link_kwargs)
        print self.outer_endpoint.common_state
        return self.inner_prototype.get_link(**link_kwargs)
    
    def handle_submission(self, link, submit_kwargs):
        return self.inner_prototype.handle_submission(link, submit_kwargs)
    
    def get_url(self, **kwargs):
        return self.outer_endpoint.get_url(**kwargs)
    
    def get_url_name(self):
        return self.outer_endpoint.get_url_name()

class PublicEndpointState(EndpointState):
    #links
    #get_resource_items
    #get_namespaces
    #item
    @property
    def inner_state(self):
        return self.endpoint.get_inner_endpoint().state
    
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
                url(r'^', include(resource.urls))
            )
        return urlpatterns

class PublicSubsite(ResourceSite):
    """
    The public facing API that exposes functionality from the VirtualResourceSite/Collections API
    
    What kind of resource?
    """
    name = 'cmssite'
    application_resource_class = PublicApplicationResource
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

class PublicResource(BaseResource):
    app_name = None
    collection = None
    
    def __init__(self, **kwargs):
        super(PublicResource, self).__init__(**kwargs)
        self.api_resource = self.collection.get_collection_resource()
    
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
        breadcrumbs.append(self.get_breadcrumb())
        return breadcrumbs
    
    def get_prompt(self):
        return self.api_resource.get_prompt()

class PublicEndpoint(PublicMixin, Endpoint):
    view_point = None
    
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
            if not hasattr(self, 'inner_endpoint'):
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
        #TODO this view should do dispatch_api on inner endpoint
        view = self.get_view()
        return url(self.get_url_suffix(), view, name=self.get_url_name(),)
    
    def get_link_prototypes(self):
        if not hasattr(self, '_link_prototypes'):
            self._link_prototypes = dict()
            for key, proto in self.get_inner_endpoint().get_link_prototypes().iteritems():
                self._link_prototypes[key] = ChainedLinkPrototype(self, proto)
        return self._link_prototypes
    
    def get_instances(self):
        return self.get_inner_endpoint().get_resource_items()
    
    def get_resource_item(self, instance, **kwargs):
        kwargs.setdefault('endpoint', self)
        return self.get_resource_item_class()(instance=instance, **kwargs)
    
    def get_resource_items(self):
        instances = self.get_instances()
        return [self.get_resource_item(instance) for instance in instances]
