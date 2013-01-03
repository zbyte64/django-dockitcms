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
    name = 'hyperadmin'
    api_endpoint = None
    
    def __init__(self, **kwargs):
        super(ResourceSubsite, self).__init__(**kwargs)
        #TODO media type handler that pumps to the endpoint
        self.register_builtin_media_types()
    
    def post_resource_registration(self, resource):
        return #No app objects in this API yet...

class PublicResource(BaseResource):
    app_name = None
    collection = None
    
    def __init__(self, **kwargs):
        super(PublicResource, self).__init__(**kwargs)
        self.api_resource = self.collection.get_collection_resource()
    
    def register_endpoint(self, endpoint):
        self.endpoints[endpoint.name_suffix] = endpoint
    
    def get_resource_name(self):
        return self.collection.title
    
    #TODO proxy links & items
