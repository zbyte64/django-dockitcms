from dockit import schema

SCHEMA_MIXINS = {}
COLLECTION_MIXINS = {}
VIEW_POINT_MIXINS = {}
INDEX_MIXINS = {}

class SchemaDefMixin(schema.Schema):
    #_mixins = dict() #define on a document that implements mixins
    
    @classmethod
    def register_schema_mixin(cls, mixin):
        cls._mixins[mixin._meta.schema_key] = mixin
        cls._meta.fields.update(mixin._meta.fields)
    
    @classmethod
    def get_active_mixins(cls, instance=None):
        return cls._mixins.values()

class MixinEventFunction(object):
    def __init__(self, instance, func, definition):
        self.instance = instance
        self.func = func
        self.definition = definition
    
    def __call__(self, *args, **kwargs):
        ret = self.func(*args, **kwargs)
        event = self.definition['event']
        event_kwargs = {self.definition['keyword']: ret}
        self.instance.send_mixin_event(event, **event_kwargs)
        return ret

class EventMixin(object):
    mixin_function_events = {} #function: {event: '', keyword: ''}
    
    def get_active_mixin(self):
        raise NotImplementedError #implented by whoever inherits
    
    def send_mixin_event(self, event, kwargs):
        '''
        The view calls this to notify the mixins that an event has happened
        '''
        mixins = self.get_active_mixins(self)
        results = []
        for mixin_cls in mixins:
            if not hasattr(mixin_cls, 'handle_mixin_event'):
                continue
            #TODO make mixins somether other then a schema
            mixin = mixin_cls(_primitive_data=self._primitive_data)
            val = mixin.handle_mixin_event(event, kwargs)
            results.append((mixin, val))
        return results
    
    def __getattribute__(self, name):
        function_events = object.__getattribute__(self, 'mixin_function_events')
        ret = object.__getattribute__(self, name)
        if name in function_events:
            return MixinEventFunction(self, ret, function_events[name])
        return ret

