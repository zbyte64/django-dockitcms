from dockit import schema
from dockit.schema import get_base_document

from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _

from design import DocumentDesign
from mixin import SchemaDefMixin, COLLECTION_MIXINS

class Application(schema.Document):
    name = schema.CharField()
    
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
        choices.append((key, value._meta.verbose_name))
    return choices

class Collection(DocumentDesign, SchemaDefMixin):
    application = schema.ReferenceField(Application)
    key = schema.SlugField(unique=True)
    mixins = schema.SetField(schema.CharField(), choices=mixin_choices, blank=True)
    admin_options = schema.SchemaField(AdminOptions)
    
    _mixins = dict()
    
    def save(self, *args, **kwargs):
        ret = super(Collection, self).save(*args, **kwargs)
        self.register_collection()
        return ret
    
    def get_collection_name(self):
        return 'dockitcms.virtual.%s' % self.key
    
    def get_document_kwargs(self, **kwargs):
        kwargs = super(Collection, self).get_document_kwargs(**kwargs)
        kwargs.setdefault('attrs', dict())
        parents = list(kwargs.get('parents', list()))
        
        active_mixins = dict()
        
        for mixin in self.mixins:
            mixin_cls = COLLECTION_MIXINS.get(mixin, None)
            if mixin_cls:
                parents.append(mixin_cls)
                active_mixins[mixin] = mixin_cls
        
        if active_mixins:
            parents.append(SchemaDefMixin)
        if parents and not any([issubclass(parent, schema.Document) for parent in parents]):
            parents.append(schema.Document)
        if parents:
            kwargs['parents'] = tuple(parents)
        if active_mixins:
            kwargs['attrs']['_mixins'] = active_mixins
        if self.application:
            kwargs['app_label'] = self.application.name
        
        def get_manage_urls(instance):
            base_url = self.get_admin_manage_url()
            urls = {'add': base_url + 'add/',
                    'list': base_url,}
            if instance.pk:
                urls['edit'] = base_url + instance.pk + '/'
            return urls
        
        kwargs['attrs']['get_manage_urls'] = get_manage_urls
        return kwargs
    
    def register_collection(self):
        doc = DocumentDesign.get_document(self, virtual=False, verbose_name=self.title, collection=self.get_collection_name())
        return doc
    
    def get_document(self):
        key = self.get_collection_name()
        #TODO how do we know if we should recreate the document? ie what if the design was modified on another node
        try:
            return get_base_document(key)
        except KeyError:
            doc = self.register_collection()
            return doc
    
    @permalink
    def get_admin_manage_url(self):
        return ('admin:dockitcms_collection_manage', [self.pk], {})
    
    def admin_manage_link(self):
        url = self.get_admin_manage_url()
        return u'<a href="%s">%s</a>' % (url, _('Manage'))
    admin_manage_link.short_description = _('Manage')
    admin_manage_link.allow_tags = True
    
    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return self.__repr__()

