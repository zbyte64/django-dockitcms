from django.conf import settings
try:
    import importlib
except ImportError:
    from django.utils import importlib

SCOPE_PROCESSORS = list()

for entry in getattr(settings, 'SCOPE_PROCESSORS', []):
    module_name, class_name = entry.rsplit('.', 1)
    module = importlib.import_module(module_name)
    obj = getattr(module, class_name)
    if isinstance(obj, type):
        obj = obj()
    SCOPE_PROCESSORS.append(obj)

