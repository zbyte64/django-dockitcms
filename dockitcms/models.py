from dockit.schema import create_document, get_schema
import dockit

from django.utils.translation import ugettext_lazy as _

from common import REGISTERED_VIEW_POINTS
from properties import GenericViewPointEntryField

from schemamaker.models import DocumentDesign

class ViewPoint(dockit.Schema):
    url = dockit.CharField()
    view_type = dockit.CharField()
    
    def get_absolute_url(self):
        return self.url
    
    def get_view_instance(self):
        return REGISTERED_VIEW_POINTS[self.view_type]
    
    def dispatch(self, request, collection):
        view_instance = REGISTERED_VIEW_POINTS[self.view_type]
        return view_instance.dispatch(request, collection, self)
    
    def __unicode__(self):
        if self.url:
            return self.url
        else:
            return self.__repr__()

class Collection(dockit.Document):
    title = dockit.CharField()
    key = dockit.SlugField(unique=True)
    schema_definition = dockit.ReferenceField(DocumentDesign)
    object_label = dockit.CharField(blank=True)
    view_points = dockit.ListField(GenericViewPointEntryField(), blank=True)
    #TODO add field for describing the label
    
    def save(self, *args, **kwargs):
        ret = super(Collection, self).save(*args, **kwargs)
        self.register_collection()
        self.register_view_points()
        return ret
    
    def get_collection_name(self):
        return 'dockitcms.virtual.%s' % self.key
    
    def register_collection(self):
        name = str(self.key)
        fields = self.schema_definition.get_fields()
        document = create_document(name, fields, module='dockitcms.models', collection=self.get_collection_name())
        
        def __unicode__(instance):
            if not self.object_label:
                return repr(instance)
            try:
                return self.object_label % instance
            except (KeyError, TypeError):
                return repr(instance)
        
        document.__unicode__ = __unicode__
        return document
    
    def register_view_points(self):
        for view_point in self.view_points:
            assert isinstance(view_point, ViewPoint)
            view_point.get_view_instance().register_view_point(self, view_point)
    
    def get_document(self):
        key = self.get_collection_name()
        try:
            return get_schema(key)
        except KeyError:
            doc = self.register_collection()
            self.register_view_points()
            return doc
    
    def admin_manage_link(self):
        from django.core.urlresolvers import reverse
        url = reverse('admin:dockitcms-collection_manage', args=[self.pk])
        return u'<a href="%s">%s</a>' % (url, _('Manage'))
    admin_manage_link.short_description = _('Manage')
    admin_manage_link.allow_tags = True
    
    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return self.__repr__()

import viewpoints
