from dockit.schema.schema import create_document
from dockit import schema

from copy import copy

SCHEMA_MIXINS = {}
INDEX_MIXINS = {}

class MixinEventFunction(object):
    def __init__(self, instance, func, definition):
        self.instance = instance
        self.func = func
        self.definition = definition
    
    def __call__(self, *args, **kwargs):
        ret = self.func(*args, **kwargs)
        event = self.definition['event']
        event_kwargs = {self.definition['keyword']: ret}
        self.instance.send_mixin_event(event, event_kwargs)
        return ret

class EventMixin(object):
    mixin_function_events = {} #function: {event: '', keyword: ''}
    
    @classmethod
    def register_mixin(self, key, mixin_class):
        raise NotImplementedError
    
    @classmethod
    def get_available_mixins(self):
        raise NotImplementedError
    
    def get_active_mixins(self):
        #return a list of instantiated mixins
        raise NotImplementedError #implented by whoever inherits
    
    def send_mixin_event(self, event, kwargs):
        '''
        The view calls this to notify the mixins that an event has happened
        '''
        mixins = self.get_active_mixins()
        results = []
        for mixin in mixins:
            if not hasattr(mixin, 'handle_mixin_event'):
                continue
            val = mixin.handle_mixin_event(event, kwargs)
            results.append((mixin, val))
        return results
    
    def __getattribute__(self, name):
        function_events = object.__getattribute__(self, 'mixin_function_events')
        ret = object.__getattribute__(self, name)
        if name in function_events:
            return MixinEventFunction(self, ret, function_events[name])
        return ret

def create_document_mixin(MIXINS):
    def mixin_choices():
        choices = list()
        for key, value in MIXINS.iteritems():
            choices.append((key, value.label))
        return choices

    class MixinSchema(schema.Schema, EventMixin):
        mixins = schema.SetField(schema.CharField(), choices=mixin_choices, blank=True)
        
        @classmethod
        def register_mixin(self, key, mixin_class):
            MIXINS[key] = mixin_class
        
        @classmethod
        def get_available_mixins(self):
            return MIXINS
        
        def __getattribute__(self, name):
            function_events = object.__getattribute__(self, 'mixin_function_events')
            if name in function_events:
                return EventMixin.__getattribute__(self, name)
            return schema.Schema.__getattribute__(self, name)
        
        def get_active_mixins(self): #CONSIDER: this modifies the fields we have
            mixins = list()
            available_mixins = self.get_available_mixins()
            for mixin_key in self.mixins:
                if mixin_key in available_mixins:
                    mixin_cls = available_mixins[mixin_key]
                    mixins.append(mixin_cls(self))
            return mixins
        
        @classmethod
        def to_python(cls, val, parent=None):
            #chicken and egg problem
            self = schema.Document.to_python(cls, val, parent)
            original_fields = self._meta.fields.keys()
            document_kwargs = {
                'fields':copy(self._meta.fields),
                'proxy': True,
                'name': cls.__name__,
            }
            self.send_mixin_event('document_kwargs', {'document_kwargs':document_kwargs})
            if original_fields != document_kwargs['fields'].keys():
                new_cls = create_document(**document_kwargs)
                return schema.Document.to_python(new_cls, val, parent)
            return self
    
    return MixinSchema

