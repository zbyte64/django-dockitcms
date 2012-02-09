from django.db.models import permalink
from dockit.schema import get_schema
import dockit

from django.utils.translation import ugettext_lazy as _

from dockit.schema.schema import create_schema

from django.utils.datastructures import SortedDict

from properties import SchemaDesignChoiceField

class FieldEntry(dockit.Schema):
    '''
    This schema is extended by others to define a field entry
    '''
    name = dockit.SlugField()
    
    field_class = None
    
    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.field_type)
    
    def get_field_kwargs(self):
        kwargs = self.to_primitive(self)
        kwargs.pop('field_type', None)
        kwargs.pop('name', None)
        if kwargs.get('verbose_name', None) == '':
            del kwargs['verbose_name']
        for key in kwargs.keys():
            if key not in self._meta.fields:
                kwargs.pop(key)
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
    
    def get_schema(self):
        fields = self.get_fields()
        if self.inherit_from:
            parent = self._meta.fields['inherit_from'].get_schema(self.inherit_from)
            if parent:
                parents = (parent, )
                schema = create_schema('temp_schema', fields, module='dockitcms.models', parents=parents)
            else:
                schema = create_schema('temp_schema', fields, module='dockitcms.models')
        else:
            schema = create_schema('temp_schema', fields, module='dockitcms.models')
        
        def __unicode__(instance):
            if not self.object_label:
                return repr(instance)
            try:
                return self.object_label % instance
            except (KeyError, TypeError):
                return repr(instance)
        
        schema.__unicode__ = __unicode__
        return schema

class SchemaEntry(FieldEntry, DesignMixin):
    inherit_from = SchemaDesignChoiceField(blank=True)
    fields = dockit.ListField(dockit.SchemaField(FieldEntry))
    object_label = dockit.CharField(blank=True)
    
    class Meta:
        proxy = True

class DocumentDesign(dockit.Document, DesignMixin):
    title = dockit.CharField()
    inherit_from = SchemaDesignChoiceField(blank=True)
    fields = dockit.ListField(dockit.SchemaField(FieldEntry))
    object_label = dockit.CharField(blank=True)
    
    def __unicode__(self):
        return self.title or ''


class ViewPoint(dockit.Document):
    url = dockit.CharField()
    
    def get_absolute_url(self):
        return self.url
    
    #TODO this is currently only called during the save
    def register_view_point(self):
        pass
    
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
        return CMSURLResolver(r'^'+self.url, urls)
    
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

class Collection(dockit.Document):
    title = dockit.CharField()
    key = dockit.SlugField(unique=True)
    schema_definition = dockit.ReferenceField(DocumentDesign)
    #TODO add field for describing the label
    
    def save(self, *args, **kwargs):
        ret = super(Collection, self).save(*args, **kwargs)
        self.register_collection()
        return ret
    
    def get_collection_name(self):
        return 'dockitcms.virtual.%s' % self.key
    
    def register_collection(self):
        name = str(self.key)
        schema = self.schema_definition.get_schema()
        
        class GeneratedCollection(dockit.Document, schema):
            __module__ = 'dockitcms.models'
            
            class Meta:
                collection = self.get_collection_name()
                verbose_name = self.title
        
        return GeneratedCollection
    
    def get_document(self):
        key = self.get_collection_name()
        #TODO how do we know if we should recreate the document? ie what if the design was modified on another node
        try:
            return get_schema(key)
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

