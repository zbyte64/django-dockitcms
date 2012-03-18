from dockit.schema.schema import create_document
from dockit import schema

SCHEMA_MIXINS = {}

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
    
    def _mixin_function(self, ret, func):
        return MixinEventFunction(self, ret, func)
    
    def __getattribute__(self, name):
        function_events = object.__getattribute__(self, 'mixin_function_events')
        ret = object.__getattribute__(self, name)
        if name in function_events:
            self._mixin_function(ret, function_events[name])
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
        
        def get_active_mixins(self, target=None): #CONSIDER: this modifies the fields we have
            mixins = list()
            target = target or self
            available_mixins = self.get_available_mixins()
            for mixin_key in self.mixins:
                if mixin_key in available_mixins:
                    mixin_cls = available_mixins[mixin_key]
                    mixins.append(mixin_cls(target))
            return mixins
        
        def make_bound_schema(self):
            if getattr(self, '_mixin_bound', False):
                return type(self)
            
            original_fields = self._meta.fields.keys()
            
            def get_active_mixins(kls, target=None):
                return self.get_active_mixins(target=target)
            
            def send_mixin_event(kls, event, kwargs):
                return self.send_mixin_event(event, kwargs)
            
            document_kwargs = {
                'fields':{},#copy(self._meta.fields.fields), #fields => uber dictionary, fields.fields => fields we defined
                'proxy': True,
                'name': type(self).__name__,
                'parents': (type(self),),
                'attrs': {'get_active_mixins':classmethod(get_active_mixins),
                          'send_mixin_event':classmethod(send_mixin_event),
                          '_mixin_bound':True},
            }
            self.send_mixin_event('document_kwargs', {'document_kwargs':document_kwargs})
            new_cls = create_document(**document_kwargs)
            assert self._meta.fields.keys() == original_fields
            return new_cls
        
        @classmethod
        def to_python(cls, val, parent=None):
            #chicken and egg problem
            #hack because super(cls).to_python does not work
            original_to_python = schema.Document.to_python.im_func
            self = original_to_python(cls, val, parent)
            if getattr(cls, '_mixin_bound', False):
                return self
            else:
                new_cls = self.make_bound_schema()
                return original_to_python(new_cls, val, parent)
    
    return MixinSchema

