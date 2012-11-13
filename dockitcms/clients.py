from hyperadminclient.clients import HyperAdminClient

from dockitcms.resources.signals import post_api_reload


class ReloadableClient(object):
    def __init__(self, **kwargs):
        super(ReloadableClient, self).__init__(**kwargs)
        self.register_listener()
    
    def reload_site(self):
        pass
        #self.api_endpoint = deepcopy(self._original_api_endpoint)
    
    def register_listener(self):
        post_api_reload.connect(self.handle_api_reload_signal, sender=self.api_endpoint)
    
    def handle_api_reload_signal(self, **kwargs):
        self.reload_site()

class CMSClient(ReloadableClient, HyperAdminClient):
    pass
