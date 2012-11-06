from dockit.schema.schema import create_document
from dockit import schema

SCHEMA_MIXINS = {}

class ManageUrlsMixin(object):
    """
    Links the document to the resource
    """
    @classmethod
    def get_admin_client(cls):
        #TODO this should be configurable
        from hyperadminclient.urls import admin_client
        return admin_client.api_endpoint
    
    @classmethod
    def get_resource(cls):
        admin_client = cls.get_admin_client()
        try:
            return admin_client.get_resource(cls)
        except Exception, error:
            for key, resource in admin_client.registry.iteritems():
                if isinstance(key, type) and issubclass(cls, key):
                    return resource
    
    def get_manage_urls(self):
        resource = self.get_resource()
        
        if resource is None:
            return {}
        
        urls = {'add': resource.get_create_link().get_absolute_url(),
                'list': resource.get_resource_link().get_absolute_url(),}
        if self.pk:
            resource_item = resource.get_resource_item(self)
            urls['edit'] = resource_item.get_absolute_url()
        return urls
    
    def get_resource_item(self):
        return self.get_resource().get_resource_item(self)

class VirtualManageUrlsMixin(ManageUrlsMixin):
    @classmethod
    def get_admin_client(cls):
        #TODO this should be configurable
        from dockitcms.urls import admin_client
        return admin_client.api_endpoint
    
    @classmethod
    def get_resource(cls):
        admin_client = cls.get_admin_client()
        try:
            return admin_client.get_resource(cls)
        except Exception, error:
            for key, resource in admin_client.registry.iteritems():
                if isinstance(key, type) and issubclass(cls, key):
                    return resource
                #TODO why do we need this?
                if issubclass(key, schema.Document) and key._meta.collection == cls._meta.collection:
                    return resource

class MixinEventWrapper(object):
    def __init__(self, instance, func, definition):
        self.instance = instance
        self.func = func
        self.definition = definition
    
    def __call__(self, *args, **kwargs):
        if 'pre' in self.definition:
            self.definition['pre'].call(self.instance, args, kwargs)
        ret = self.func(*args, **kwargs)
        if 'collect' in self.definition:
            ret = self.definition['collect'].call(self.instance, args, kwargs, ret)
        if 'post' in self.definition:
            c_ret = self.definition['post'].call(self.instance, args, kwargs, ret)
            if c_ret is not None:
                ret = c_ret
        return ret
        
        event = self.definition['event']
        event_kwargs = {self.definition['keyword']: ret}
        self.instance.send_mixin_event(event, event_kwargs)
        return ret

class BaseEventFunction(object):
    def __init__(self, event):
        self.event = event

class PreEventFunction(BaseEventFunction):
    def call(self, instance, args, kwargs):
        event_kwargs = dict(kwargs)
        instance.send_mixin_event(self.event, event_kwargs)

class CollectEventFunction(BaseEventFunction):
    def __init__(self, event, extend_function='extend'):
        super(CollectEventFunction, self).__init__(event)
        self.extend_function_name = extend_function
    
    def call(self, instance, args, kwargs, ret):
        event_kwargs = dict(kwargs)
        results = instance.send_mixin_event(self.event, event_kwargs)
        for mixin, val in results:
            if val is not None:
                getattr(ret, self.extend_function_name)(val)
        return ret

class PostEventFunction(BaseEventFunction):
    def __init__(self, event, keyword=None):
        super(PostEventFunction, self).__init__(event)
        self.keyword = keyword
    
    def call(self, instance, args, kwargs, ret):
        event_kwargs = dict(kwargs)
        if self.keyword:
            event_kwargs[self.keyword] = ret
        instance.send_mixin_event(self.event, event_kwargs)

class EventMixin(object):
    mixin_function_events = {}
    '''
    function: {pre: PreEventFunction(event=''), #passes in function kwargs to event
               collect: CollectEventFunction(event='', extend_function='extends'), #extends the return function
               post: PostEventFunction(event='', keyword=''),
               TODO: post: ChainedEventFuncion(PostEventFunction(event='', keyword=''), PostEventFunction(event='', keyword=''))} #two event slots
    '''
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
        return MixinEventWrapper(self, ret, func)
    
    def __getattribute__(self, name):
        function_events = object.__getattribute__(self, 'mixin_function_events')
        ret = object.__getattribute__(self, name)
        if name in function_events:
            return self._mixin_function(ret, function_events[name])
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
            
            cls = type(self)
            
            document_kwargs = {
                'fields':{},#copy(self._meta.fields.fields), #fields => uber dictionary, fields.fields => fields we defined
                'proxy': True,
                'name': cls.__name__,
                'parents': (cls,),
                'module': cls.__module__,
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

