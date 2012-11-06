import datetime

from dockitcms.loading.base import SiteReloader

from django.core.cache import cache


CACHE_KEY = 'key'

class CacheMixin(object):
    def get_cache_key(self):
        return CACHE_KEY

class SiteCacheReload(CacheMixin, SiteReloader):
    def signal_reload(self):
        key = self.get_cache_key()
        cache.set(key, datetime.datetime.now())
    
    #TODO middleware that checks cache value

class SiteCacheReloadMiddleware(CacheMixin, object):
    def process_request(self, request):
        key = self.get_cache_key()
        val = cache.get(key)
        if getattr(self, 'previous_cache_value', None) != val:
            self.previous_cache_value = val
            from dockitcms.sites import site
            site.reload_site()

