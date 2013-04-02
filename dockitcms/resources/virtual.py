'''
Defines resources for virtual collections and applications.
Virtual resources are contained by their own resource site and is reloaded when the CMS signals an application reload
'''
from hyperadmin.sites import ResourceSite

from dockitcms.models import Collection, Application
from dockitcms.resources.signals import post_api_reload


class VirtualResourceSite(ResourceSite):
    """
    An API composed of the collections & applications defined through the core API.
    AKA: Collections API
    """
    def __init__(self, name='dockitcms-hyperadmin', **kwargs):
        super(VirtualResourceSite, self).__init__(name=name, **kwargs)
    
    def query_applications(self):
        return Application.objects.all()
    
    def query_collections(self):
        return Collection.objects.all()
    
    def load_applications(self):
        for app in self.query_applications():
            try:
                self.register_application(app.slug, resource_name=app.name, base_url_name_prefix=app.slug)
            except Exception as error:
                self.get_logger().exception('Could not register application')
    
    def load_collections(self):
        self.registry = dict()
        for collection in self.query_collections():
            try:
                object_class = collection.get_object_class()
                resource_class = collection.get_resource_class()
                app_name = collection.application.slug
                #TODO all collections get a slug or key
                if getattr(collection, 'key', None):
                    self.register(object_class, resource_class, collection=collection, app_name=app_name, resource_slug=collection.key)
                else:
                    self.register(object_class, resource_class, collection=collection, app_name=app_name)
            except Exception as error:
                self.get_logger().exception('Could not register collection')
    
    def load_site(self):
        self.load_applications()
        self.load_collections()
    
    def reload_site(self):
        self.load_site()
        post_api_reload.send(sender=type(self), api_site=self)

site = VirtualResourceSite()
site.register_builtin_media_types()
site.install_storage_resources()

