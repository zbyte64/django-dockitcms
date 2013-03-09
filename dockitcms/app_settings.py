from django.conf import settings
from django.utils.importlib import import_module

class LazyList(list):
    _loaded = False
    
    def __iter__(self):
        if not self._loaded:
            self.load()
        return list.__iter__(self)
    
    def load(self):
        for entry in getattr(settings, 'SCOPE_PROCESSORS', []):
            module_name, class_name = entry.rsplit('.', 1)
            module = import_module(module_name)
            obj = getattr(module, class_name)
            if isinstance(obj, type):
                obj = obj()
            self.append(obj)
        self._loaded = True

SCOPE_PROCESSORS = LazyList()

path = getattr(settings, 'SITE_RELOADER', 'dockitcms.loading.base.SiteReloader')
path, classname = path.rsplit('.', 1)

SITE_RELOADER = getattr(import_module(path), classname)()

SITE_RELOADER_CACHE_KEY = getattr(settings, 'SITE_RELOADER_CACHE_KEY', 'dockitcms.reloader')
