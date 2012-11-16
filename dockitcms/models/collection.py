from dockit import schema
from dockit.schema import get_base_document
from dockit.schema.loading import force_register_documents

from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from dockitcms.models.design import DocumentDesign
from dockitcms.models.mixin import ManageUrlsMixin, VirtualManageUrlsMixin, EventMixin, PostEventFunction

COLLECTION_MIXINS = {}

class Application(schema.Document):
    name = schema.CharField()
    slug = schema.SlugField(unique=True)
    
    def create_natural_key(self):
        return {'slug':self.slug}
    
    def __unicode__(self):
        return self.name

class AdminOptions(schema.Schema):
    list_display = schema.ListField(schema.CharField(), blank=True)
    list_per_page = schema.IntegerField(default=100)
    #raw_id_fields = schema.ListField(schema.CharField(), blank=True)
    #readonly_fields = schema.ListField(schema.CharField(), blank=True)

def mixin_choices():
    choices = list()
    for key, value in COLLECTION_MIXINS.iteritems():
        choices.append((key, value.label))
    return choices

class Collection(ManageUrlsMixin, schema.Document):
    application = schema.ReferenceField(Application)
    admin_options = schema.SchemaField(AdminOptions)
    title = None
    
    public_resource_class = None #TODO implement this, must have register_endpoint
    
    @permalink
    def get_admin_manage_url(self):
        return self.get_resource_item().get_absolute_url()
    
    def admin_manage_link(self):
        url = self.get_admin_manage_url()
        return u'<a href="%s">%s</a>' % (url, _('Manage'))
    admin_manage_link.short_description = _('Manage')
    admin_manage_link.allow_tags = True
    
    def get_object_class(self):
        raise NotImplementedError
    
    def get_resource_class(self):
        raise NotImplementedError
    
    @classmethod
    def get_collection_admin_client(cls):
        #TODO this should be configurable
        from dockitcms.urls import admin_client
        return admin_client.api_endpoint
    
    def get_collection_resource(self):
        admin_client = self.get_collection_admin_client()
        cls = self.get_object_class()
        try:
            return admin_client.get_resource(cls)
        except Exception, error:
            seen = list()
            for key, resource in admin_client.registry.iteritems():
                seen.append((resource.collection.collection_type, key, resource.collection))
                if resource.collection.collection_type != 'dockitcms.virtualdocument':
                    assert False, str("%s, %s, %s, %s" % (resource.collection, self, resource.collection==self, resource.collection.collection_type))
                if hasattr(resource, 'collection') and resource.collection == self:
                    return resource
            assert False, str(seen)
    
    def get_public_resource_class(self):
        return self.public_resource_class
    
    def get_public_resource_options(self):
        return {
            'collection': self,
        }
    
    def register_public_resource(self, site):
        klass = self.get_public_resource_class()
        options = self.get_public_resource_options()
        #resource_adaptor = self.get_object_class()
        resource_adaptor = self.get_collection_resource().resource_adaptor
        return site.register(resource_adaptor, klass, **options)
    
    class Meta:
        typed_field = 'collection_type'
        verbose_name = 'collection'

class VirtualDocumentCollection(Collection, DocumentDesign, EventMixin):
    key = schema.SlugField(unique=True)
    mixins = schema.SetField(schema.CharField(), choices=mixin_choices, blank=True)
    
    mixin_function_events = {
        'get_document_kwargs': {
            'post': PostEventFunction(event='document_kwargs', keyword='document_kwargs')
        },
    }
    
    @classmethod
    def register_mixin(self, key, mixin_class):
        COLLECTION_MIXINS[key] = mixin_class
    
    @classmethod
    def get_available_mixins(self):
        return COLLECTION_MIXINS
    
    def __getattribute__(self, name):
        function_events = object.__getattribute__(self, 'mixin_function_events')
        if name in function_events:
            ret = object.__getattribute__(self, name)
            return self._mixin_function(ret, function_events[name])
        return Collection.__getattribute__(self, name)
    
    def get_active_mixins(self):
        mixins = list()
        available_mixins = self.get_available_mixins()
        for mixin_key in self.mixins:
            if mixin_key in available_mixins:
                mixin_cls = available_mixins[mixin_key]
                mixins.append(mixin_cls(self))
        return mixins
    
    def save(self, *args, **kwargs):
        ret = super(VirtualDocumentCollection, self).save(*args, **kwargs)
        self.register_collection()
        return ret
    
    def get_collection_name(self):
        return 'dockitcms.virtual.%s' % self.key
    
    def get_document_kwargs(self, **kwargs):
        kwargs = super(VirtualDocumentCollection, self).get_document_kwargs(**kwargs)
        kwargs.setdefault('attrs', dict())
        parents = list(kwargs.get('parents', list()))
        
        parents.append(VirtualManageUrlsMixin)
        if not any([issubclass(parent, schema.Document) for parent in parents]):
            parents.append(schema.Document)
        
        if parents:
            kwargs['parents'] = tuple(parents)
        if self.application:
            kwargs['app_label'] = self.application.name
        
        kwargs['attrs']['_collection_document'] = self
        return kwargs
    
    def register_collection(self):
        doc = DocumentDesign.get_document(self, virtual=False, verbose_name=self.title, collection=self.get_collection_name())
        force_register_documents(doc._meta.app_label, doc)
        return doc
    
    def get_document(self):
        key = self.get_collection_name()
        #TODO how do we know if we should recreate the document? ie what if the design was modified on another node
        try:
            return get_base_document(key)
        except KeyError:
            doc = self.register_collection()
            return doc
    
    def get_object_class(self):
        return self.get_document()
    
    def get_resource_class(self):
        from dockitcms.resources.collection import VirtualDocumentResource
        return VirtualDocumentResource
    
    def get_collection_resource(self):
        admin_client = self.get_collection_admin_client()
        cls = self.get_object_class()
        try:
            return admin_client.get_resource(cls)
        except Exception, error:
            for key, resource in admin_client.registry.iteritems():
                if isinstance(key, type) and issubclass(cls, key):
                    return resource
                #TODO why do we need this?
                if issubclass(key, schema.Document) and key._meta.collection == cls._meta.collection:
                    return resource
    
    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return self.__repr__()
    
    class Meta:
        typed_key = 'dockitcms.virtualdocument'

class ModelCollection(Collection, EventMixin):
    model = schema.ModelReferenceField(ContentType)
    
    def get_model(self):
        return self.model.model_class()
    
    def get_object_class(self):
        return self.get_model()
    
    def get_resource_class(self):
        from dockitcms.resources.collection import ModelResource
        return ModelResource
    
    class Meta:
        typed_key = 'dockitcms.model'

#TODO add ResourceCollection which points to an existing resource

