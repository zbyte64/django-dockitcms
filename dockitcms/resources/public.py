"""
Resource classes for powering the public facing API go here. Typically these classes are for reimplementing the Collections API
"""
from hyperadmin.sites import ResourceSite
from hyperadmin.resources.resources import BaseResource

from django.conf.urls.defaults import patterns, url, include


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

class ResourceSubsite(ResourceSite):
    """
    The public facing API that exposes functionality from the VirtualResourceSite/Collections API
    
    What kind of resource?
    """
    name = 'hyperadmin'
    application_resource_class = PublicApplicationResource
    api_endpoint = None
    
    def __init__(self, **kwargs):
        super(ResourceSubsite, self).__init__(**kwargs)
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
        ret = super(ResourceSubsite, self).fork(**kwargs)
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
    
    #TODO proxy links & items
