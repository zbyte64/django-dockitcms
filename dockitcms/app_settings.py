from django.conf import settings
try:
    import importlib
except ImportError:
    from django.utils import importlib

class LazyList(list):
    _loaded = False
    
    def __iter__(self):
        if not self._loaded:
            self.load()
    
    def load(self):
        for entry in getattr(settings, 'SCOPE_PROCESSORS', []):
            module_name, class_name = entry.rsplit('.', 1)
            module = importlib.import_module(module_name)
            obj = getattr(module, class_name)
            if isinstance(obj, type):
                obj = obj()
            self.append(obj)
        self._loaded = True

SCOPE_PROCESSORS = LazyList()

