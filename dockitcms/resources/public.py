"""
Resource classes for powering the public facing API go here. Typically these classes are for reimplementing the Collections API
"""
from hyperadmin.sites import ResourceSite
from hyperadmin.rsources.resources import Resource

class ResourceSubsite(ResourceSite):
    """
    The public facing API that exposes functionality from the VirtualResourceSite/Collections API
    
    What kind of resource?
    """
    def post_resource_registration(self, resource):
        return #No app objects in this API yet...

class PublicResource(Resource):
    def __init__(self, **kwargs):
        self.collection = kwargs.pop('collection')
        self.api_resource = self.collection.get_collection_resource()
        super(PublicResource, self).__init__(**kwargs)
    
    def register_endpoint(self, endpoint):
        self.endpoints[endpoint.name_suffix] = endpoint
    
    #TODO proxy links & items
