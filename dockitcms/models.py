from django.db.models import permalink
from dockit.schema import create_document, get_schema
import dockit

from django.utils.translation import ugettext_lazy as _

from schemamaker.models import DocumentDesign

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

import viewpoints
