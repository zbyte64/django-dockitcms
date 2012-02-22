from django.contrib.sites.models import Site

from app_settings import SCOPE_PROCESSORS

class Scope(object):
    '''
    As a request travels through the application, the code creates and chains scopes.
    Scopes act like a logical portal, each scope may have objects and context attached that may be used at rendering time.
    Typically we can expect the following scopes:
        * site
        * subsite
        * view point
        * (optionally) collection or object
    '''
    def __init__(self, name, **kwargs):
        self.name = name
        self.kwargs = kwargs
        self.data = dict()
        
        self.execute_scope_processors()
    
    def execute_scope_processors(self):
        for processor in self.get_scope_processors():
            processor(self)
    
    def get_scope_processors(self):
        return SCOPE_PROCESSORS
    
    def add_data(self, key, data, admin_url=None):
        data = ScopeData(key=key, data=data, admin_url=admin_url)
        self.data[key] = data

class ScopeData(object):
    def __init__(self, key, data, admin_url):
        self.key = key
        self.data = data
        self.admin_url = admin_url

def get_site_scope():
    obj = Site.objects.get_current()
    return Scope(name='site', object=obj)

