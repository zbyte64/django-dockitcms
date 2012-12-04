"""
Resource classes for powering the public facing API go here. Typically these classes are for reimplementing the Collections API
"""
from hyperadmin.sites import ResourceSite
from hyperadmin.resources.resources import BaseResource

class ResourceSubsite(ResourceSite):
    """
    The public facing API that exposes functionality from the VirtualResourceSite/Collections API
    
    What kind of resource?
    """
    def __init__(self, api_endpoint, name='hyperadmin'):
        self.api_endpoint = api_endpoint
        super(ResourceSubsite, self).__init__(name=name)
        #TODO media type handler that pumps to the endpoint
        self.register_builtin_media_types()
    
    def post_resource_registration(self, resource):
        return #No app objects in this API yet...

class PublicResource(BaseResource):
    def __init__(self, **kwargs):
        self.collection = kwargs.pop('collection')
        self._app_name = kwargs.pop('app_name')
        self.api_resource = self.collection.get_collection_resource()
        super(PublicResource, self).__init__(**kwargs)
    
    def register_endpoint(self, endpoint):
        self.endpoints[endpoint.name_suffix] = endpoint
    
    def get_app_name(self):
        return self._app_name
    app_name = property(get_app_name)
    
    def get_resource_name(self):
        return self.collection.title
    
    #TODO proxy links & items
