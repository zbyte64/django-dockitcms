from dockit.schema.schema import create_schema, create_document
from dockit.schema import get_base_document
from dockit import schema

from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst
from django.utils.datastructures import SortedDict
from django.db.models import permalink
from django.contrib.sites.models import Site

from properties import SchemaDesignChoiceField
from scope import Scope

import re
import urlparse

class SchemaDefMixin(schema.Schema):
    #_mixins = dict() #define on a document that implements mixins
    
    @classmethod
    def register_schema_mixin(cls, mixin):
        cls._mixins[mixin._meta.schema_key] = mixin
        cls._meta.fields.update(mixin._meta.fields)
    
    @classmethod
    def get_active_mixins(cls, instance=None):
        return cls._mixins.values()

class FieldEntry(schema.Schema):
    '''
    This schema is extended by others to define a field entry
    '''
    name = schema.SlugField()
    
    field_class = None
    
    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.field_type)
    
    def get_field_kwargs(self):
        kwargs = self.to_primitive(self)
        kwargs.pop('field_type', None)
        kwargs.pop('name', None)
        if kwargs.get('verbose_name', None) == '':
            del kwargs['verbose_name']
        for key, value in kwargs.items():
            if key not in self._meta.fields:
                kwargs.pop(key)
            else:
                kwargs[str(key)] = value
        return kwargs
    
    def create_field(self):
        kwargs = self.get_field_kwargs()
        return self.field_class(**kwargs)
    
    def get_scaffold_example(self, context, varname):
        raise NotImplementedError
    
    class Meta:
        typed_field = 'field_type'

class DesignMixin(object):
    def get_fields(self):
        fields = SortedDict()
        for field_entry in self.fields:
            assert field_entry.name
            field = field_entry.create_field()
            fields[field_entry.name] = field
        return fields
    
    def get_schema_name(self):
        return 'temp_schema'
    
    def get_schema_kwargs(self, **kwargs):
        params = {'module':'dockitcms.models',
                  'virtual':True,
                  'fields':self.get_fields(),
                  'name':self.get_schema_name(),}
        attrs = {}
        if self.object_label:
            def __unicode__(instance):
                try:
                    return self.object_label % instance
                except (KeyError, TypeError):
                    return repr(instance)
            attrs['__unicode__'] = __unicode__
        params.update(kwargs)
        params.setdefault('attrs', {})
        params['attrs'].update(attrs)
        return params
    
    def get_document_kwargs(self, **kwargs):
        return self.get_schema_kwargs(**kwargs)
    
    def get_schema(self, **kwargs):
        params = self.get_schema_kwargs(**kwargs)
        return create_schema(**params)
    
    def get_document(self, **kwargs):
        params = self.get_document_kwargs(**kwargs)
        doc = create_document(**params)
        if not issubclass(doc, schema.Document):
            raise TypeError("Did not properly create a document")
        return doc

class SchemaEntry(FieldEntry, DesignMixin):
    #inherit_from = SchemaDesignChoiceField(blank=True)
    fields = schema.ListField(schema.SchemaField(FieldEntry))
    object_label = schema.CharField(blank=True)
    
    class Meta:
        proxy = True

class DocumentDesign(schema.Document, DesignMixin):
    title = schema.CharField()
    inherit_from = SchemaDesignChoiceField(blank=True)
    fields = schema.ListField(schema.SchemaField(FieldEntry), blank=True)
    object_label = schema.CharField(blank=True)
    
    def __unicode__(self):
        return self.title or ''
    
    def get_schema_name(self):
        return str(''.join([capfirst(part) for part in self.title.split()]))
    
    def get_document_kwargs(self, **kwargs):
        kwargs = DesignMixin.get_document_kwargs(self, **kwargs)
        if self.inherit_from:
            parent = self._meta.fields['inherit_from'].get_schema(self.inherit_from)
            if parent:
                if issubclass(parent, schema.Document):
                    kwargs['parents'] = (parent,)
                else:
                    kwargs['parents'] = (parent, schema.Document)
        return kwargs

from mixins import MIXINS

def mixin_choices():
    choices = list()
    for key, value in MIXINS.iteritems():
        choices.append((key, value._meta.verbose_name))
    return choices

class Application(schema.Document):
    name = schema.CharField()
    
    def __unicode__(self):
        return self.name

class Collection(DocumentDesign, SchemaDefMixin):
    application = schema.ReferenceField(Application)
    key = schema.SlugField(unique=True)
    mixins = schema.SetField(schema.CharField(), choices=mixin_choices, blank=True)
    
    _mixins = dict()
    
    def save(self, *args, **kwargs):
        ret = super(Collection, self).save(*args, **kwargs)
        self.register_collection()
        return ret
    
    def get_collection_name(self):
        return 'dockitcms.virtual.%s' % self.key
    
    def get_document_kwargs(self, **kwargs):
        kwargs = super(Collection, self).get_document_kwargs()
        parents = list(kwargs.get('parents', list()))
        
        active_mixins = dict()
        
        for mixin in self.mixins:
            mixin_cls = MIXINS.get(mixin, None)
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
            kwargs.setdefault('attrs', dict())
            kwargs['attrs']['_mixins'] = active_mixins
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

class Subsite(schema.Document, SchemaDefMixin):
    url = schema.CharField()
    name = schema.CharField()
    sites = schema.ModelSetField(Site, blank=True)
    
    _mixins = dict()
    
    def __unicode__(self):
        return u'%s - %s' % (self.name, self.url)

Subsite.objects.index('sites').commit()

class ViewPoint(schema.Document, SchemaDefMixin):
    subsite = schema.ReferenceField(Subsite)
    url = schema.CharField(help_text='May be a regular expression that the url has to match')
    
    _mixins = dict()
    
    @property
    def url_regexp(self):
        return re.compile(self.full_url)
    
    @property
    def full_url(self):
        return urlparse.urljoin(self.subsite.url, self.url)
    
    def get_absolute_url(self):
        return self.full_url
    
    #TODO this is currently only called during the save
    def register_view_point(self):
        pass
    
    def get_scopes(self):
        return [Scope('site', object=Site.objects.get_current()),
                Scope('subsite', object=self.subsite),
                Scope('viewpoint', object=self)]
    
    def get_admin_view(self, **kwargs):
        from dockitcms.admin.views import ViewPointDesignerFragmentView
        kwargs['view_spec'] = self
        return ViewPointDesignerFragmentView.as_view(**kwargs)
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns
        return patterns('')
    
    def get_resolver(self):
        from dockitcms.common import CMSURLResolver
        urls = self.get_urls()
        return CMSURLResolver(r'^'+self.full_url, urls)
    
    def dispatch(self, request):
        resolver = self.get_resolver()
        view_match = resolver.resolve(request.path)
        return view_match.func(request, *view_match.args, **view_match.kwargs)
    
    def reverse(self, name, *args, **kwargs):
        resolver = self.get_resolver()
        return resolver.reverse(name, *args, **kwargs)
    
    def save(self, *args, **kwargs):
        super(ViewPoint, self).save(*args, **kwargs)
        self.register_view_point()
    
    def __unicode__(self):
        if self.url:
            return self.url
        else:
            return self.__repr__()
    
    class Meta:
        typed_field = 'view_type'

ViewPoint.objects.index('subsite').commit()

import fields
import viewpoints


