import datetime

from dockitcms.loading.base import SiteReloader
from dockitcms.signals import reload_site

from django.core.cache import cache


CACHE_KEY = 'key'

class CacheMixin(object):
    def get_cache_key(self):
        #TODO drive with django settings
        return CACHE_KEY

class SiteCacheReload(CacheMixin, SiteReloader):
    '''
    Allows for multiple site nodes to stay in sync by using the cache
    framework. Install `SiteCacheReloadMiddleware` into your middleware
    to uses this.
    '''
    def request_reload(self):
        key = self.get_cache_key()
        cache.set(key, datetime.datetime.now())

class SiteCacheReloadMiddleware(CacheMixin, object):
    def process_request(self, request):
        key = self.get_cache_key()
        val = cache.get(key)
        if getattr(self, 'previous_cache_value', None) != val:
            self.previous_cache_value = val
            reload_site.send(sender=None)
