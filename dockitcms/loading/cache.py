import datetime

from dockitcms.loading.base import SiteReloader
from dockitcms.signals import reload_site
from dockitcms.app_settings import SITE_RELOADER_CACHE_KEY

from django.core.cache import cache


class CacheMixin(object):
    def get_cache_key(self):
        return SITE_RELOADER_CACHE_KEY

class CacheSiteReloader(CacheMixin, SiteReloader):
    '''
    Allows for multiple site nodes to stay in sync by using the cache
    framework. Install `CacheSiteReloaderMiddleware` into your middleware
    to uses this.
    '''
    def request_reload(self):
        key = self.get_cache_key()
        cache.set(key, datetime.datetime.now())

class CacheSiteReloaderMiddleware(CacheMixin, object):
    def process_request(self, request):
        key = self.get_cache_key()
        val = cache.get(key)
        if getattr(self, 'previous_cache_value', None) != val:
            self.previous_cache_value = val
            reload_site.send(sender=None)
