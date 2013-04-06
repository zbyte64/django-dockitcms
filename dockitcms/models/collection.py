from __future__ import unicode_literals

from dockit import schema
from dockit.schema import get_base_document

from dockit.schema.loading import force_register_documents

from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import MergeDict
from django.contrib.contenttypes.models import ContentType

from dockitcms.models.design import DocumentDesign
from dockitcms.models.mixin import ManageUrlsMixin, VirtualManageUrlsMixin, EventMixin, PostEventFunction, CollectEventFunction


class MixinDict(MergeDict):
    def __init__(self, substates=[], data={}):
        self.active_dictionary = dict()
        self.substates = substates
        dictionaries = self.get_dictionaries()
        super(MixinDict, self).__init__(*dictionaries)
        self.update(data)

    def get_dictionaries(self):
        return [self.active_dictionary] + self.substates

    def __copy__(self):
        substates = self.get_dictionaries()
        ret = self.__class__(substates=substates)
        return ret

    def __setitem__(self, key, value):
        self.active_dictionary[key] = value

    def __delitem__(self, key):
        del self.active_dictionary[key]

    def pop(self, key, default=None):
        return self.active_dictionary.pop(key, default)

    def update(self, other_dict):
        self.active_dictionary.update(other_dict)

    def choices(self):
        choices = list()
        for key, value in self.iteritems():
            choices.append((key, value.label))
        return choices

COLLECTION_MIXINS = MixinDict()
VIRTUAL_COLLECTION_MIXINS = MixinDict(substates=[COLLECTION_MIXINS])
MODEL_COLLECTION_MIXINS = MixinDict(substates=[COLLECTION_MIXINS])


class Application(schema.Document):
    name = schema.CharField()
    slug = schema.SlugField(unique=True)

    def create_natural_key(self):
        return {'slug':self.slug}

    def __unicode__(self):
        return self.name

Application.objects.index('slug').commit()

class AdminOptions(schema.Schema):
    list_display = schema.ListField(schema.CharField(), blank=True)
    list_per_page = schema.IntegerField(default=100)
    #raw_id_fields = schema.ListField(schema.CharField(), blank=True)
    #readonly_fields = schema.ListField(schema.CharField(), blank=True)

class Collection(ManageUrlsMixin, schema.Document, EventMixin):
    key = schema.SlugField(unique=True)
    application = schema.ReferenceField(Application)
    admin_options = schema.SchemaField(AdminOptions)
    title = None

    mixins = schema.SetField(schema.CharField(), choices=COLLECTION_MIXINS.choices, blank=True)

    mixin_function_events = {
        'get_document_kwargs': {
            'post': PostEventFunction(event='document_kwargs', keyword='document_kwargs'),
        },
        'get_view_endpoints': {
            'collect': CollectEventFunction(event='view_endpoints', extend_function='extends'),
            'post': PostEventFunction(event='view_endpoints', keyword='view_endpoints'),
        },
    }

    @classmethod
    def register_mixin(self, key, mixin_class):
        self.get_available_mixins()[key] = mixin_class

    @classmethod
    def get_available_mixins(self):
        return COLLECTION_MIXINS

    def __getattribute__(self, name):
        function_events = object.__getattribute__(self, 'mixin_function_events')
        if name in function_events:
            ret = object.__getattribute__(self, name)
            return self._mixin_function(ret, function_events[name])
        return schema.Document.__getattribute__(self, name)

    def get_active_mixins(self):
        mixins = list()
        available_mixins = self.get_available_mixins()
        for mixin_key in self.mixins:
            if mixin_key in available_mixins:
                mixin_cls = available_mixins[mixin_key]
                mixins.append(mixin_cls(self))
        return mixins

    @permalink
    def get_admin_manage_url(self):
        return self.get_resource_item().get_absolute_url()

    def admin_manage_link(self):
        url = self.get_admin_manage_url()
        return '<a href="%s">%s</a>' % (url, _('Manage'))
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
            return admin_client.registry[cls]
        except Exception as error:
            seen = list()
            for key, resource in admin_client.registry.iteritems():
                seen.append((resource.collection.collection_type, key, resource.collection))
                #if resource.collection.collection_type != 'dockitcms.virtualdocument':
                #    assert False, str("%s, %s, %s, %s" % (resource.collection, self, resource.collection==self, resource.collection.collection_type))
                if hasattr(resource, 'collection') and resource.collection == self:
                    return resource
            assert False, str(seen)

    def get_public_resource_class(self):
        from dockitcms.resources.public import PublicResource
        return PublicResource

    def get_public_resource_options(self, **kwargs):
        params = {
            'collection': self,
            'app_name': self.application.slug,
            'resource_adaptor': self.get_collection_resource().resource_adaptor
        }
        params.update(kwargs)
        return params

    def register_public_resource(self, site, **kwargs):
        klass = self.get_public_resource_class()
        options = self.get_public_resource_options(**kwargs)
        return site.register_endpoint(klass, **options)

    def get_view_endpoints(self):
        return []

    def register_collection(self):
        pass

    def save(self, *args, **kwargs):
        ret = super(Collection, self).save(*args, **kwargs)
        self.register_collection()
        return ret

    class Meta:
        typed_field = 'collection_type'
        verbose_name = 'collection'

Collection.objects.index('key').commit()

class VirtualDocumentCollection(Collection, DocumentDesign):
    mixins = schema.SetField(schema.CharField(), choices=VIRTUAL_COLLECTION_MIXINS.choices, blank=True)

    @classmethod
    def get_available_mixins(self):
        return VIRTUAL_COLLECTION_MIXINS

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
            return admin_client.registry[cls]
        except Exception as error:
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

class ModelCollection(Collection):
    model = schema.ModelReferenceField(ContentType)
    mixins = schema.SetField(schema.CharField(), choices=MODEL_COLLECTION_MIXINS.choices, blank=True)

    @classmethod
    def get_available_mixins(self):
        return MODEL_COLLECTION_MIXINS

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

