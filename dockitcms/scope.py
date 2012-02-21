from django.contrib.sites.models import Site

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

def get_site_scope():
    obj = Site.objects.get_current()
    return Scope(name='site', object=obj)

