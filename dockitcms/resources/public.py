# -*- coding: utf-8 -*-
'''
The basis for public facing resources that power the CMS frontend.
'''
from hyperadmin.sites import BaseResourceSite
from hyperadmin.resources import BaseResource
from hyperadmin.resources.directory import ResourceDirectory
from hyperadmin.resources.endpoints import ResourceEndpoint
from hyperadmin.links import LinkNotAvailable
from hyperadmin.states import EndpointState
from hyperadmin.resources.hyperobjects import ResourceItem
from hyperadmin.apirequests import InternalAPIRequest
from hyperadmin.app_settings import DEFAULT_API_REQUEST_CLASS

from django.conf.urls.defaults import patterns, url, include


class ChainedAPIRequest(DEFAULT_API_REQUEST_CLASS):
    def __init__(self, inner_site, **kwargs):
        super(ChainedAPIRequest, self).__init__(**kwargs)
        params = {
            'site': inner_site,
            'path': self.path,
            'url_args': [],
            'url_kwargs': {},
            'method': self.method,
            'params': self.params,
            'payload': self.payload,
            'full_path': self.get_full_path(),
            'request': self.request,
            'user': self.user,
        }
        self.inner_api_request = InternalAPIRequest(**params)
        self.inner_api_request.session_state.update(self.session_state)


class PublicEndpointState(EndpointState):
    #TODO links should consult inner_state, rewrite urls if they exist
    #get_namespaces

    #link_collector_class = PublicEndpointStateLinkCollectionProvider

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


class PublicAPIRequestBuilder(object):
    apirequest_class = ChainedAPIRequest

    def get_api_request_kwargs(self, **kwargs):
        kwargs.setdefault('inner_site', self.get_inner_site())
        return super(PublicAPIRequestBuilder, self).get_api_request_kwargs(**kwargs)


class PublicMixin(PublicAPIRequestBuilder):
    state_class = PublicEndpointState
    resource_item_class = PublicResourceItem
    inner_endpoint = None

    def get_inner_site(self):
        return self.inner_endpoint.site

    def get_inner_apirequest(self):
        return self.api_request.inner_api_request

    def get_inner_endpoint(self):
        if self.api_request:
            if not hasattr(self, 'bound_inner_endpoint'):
                inner_apirequest = self.get_inner_apirequest()
                urlname = self.get_url_name()
                self.bound_inner_endpoint = inner_apirequest.get_endpoint(urlname)
            return self.bound_inner_endpoint
        return self.inner_endpoint

    def get_base_url_name(self):
        return self.inner_endpoint.get_base_url_name()

    def get_url_suffix(self):
        ending = self.inner_endpoint.get_url_suffix()
        if ending.startswith('^'):
            ending = ending[1:]
        if self.url_suffix:
            return self.url_suffix + ending
        return ending

    def get_name_suffix(self):
        return self.inner_endpoint.get_name_suffix()

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


class PublicSubsite(PublicAPIRequestBuilder, BaseResourceSite):
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

    def get_inner_site(self):
        return self.api_endpoint


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
        if 'detail' not in self.link_prototypes:
            raise LinkNotAvailable('Link unavailable: detail')
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
        #ilp = inner_endpoint.link_prototypes
        #olp = self.link_prototypes
        return inner_endpoint.dispatch_api(self.get_inner_apirequest())

    def get_common_state(self):
        return {}
    common_state = property(get_common_state)
