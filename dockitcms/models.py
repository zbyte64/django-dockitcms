import dockit
from dockit.schema import create_document, get_schema

from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _

from fieldmaker.resource import field_registry

from common import REGISTERED_VIEW_POINTS

class SchemaDefinition(dockit.Document):
    title = dockit.CharField()
    data = dockit.ListField()
    
    def get_form_specification(self):
        return field_registry.form_specifications['base.1']
    
    def get_schema_form(self):
        form_spec = self.get_form_specification()
        return form_spec.create_form(self.data)
    
    def get_schema_fields(self):
        form_spec = self.get_form_specification()
        return form_spec.get_fields(self.data)
    
    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return self.__repr__()

class ViewPoint(dockit.Schema):
    url = dockit.CharField()
    view_class = dockit.TextField()
    view_config = dockit.DictField(blank=True)
    
    def get_absolute_url(self):
        return self.url
    
    def get_view_instance(self):
        return REGISTERED_VIEW_POINTS[self.view_class]
    
    def dispatch(self, request, collection):
        view_instance = REGISTERED_VIEW_POINTS[self.view_class]
        return view_instance.dispatch(request, collection, self)
    
    def __unicode__(self):
        if self.url:
            return self.url
        else:
            return self.__repr__()

class Collection(dockit.Document):
    title = dockit.CharField()
    key = dockit.SlugField(unique=True)
    schema_definition = dockit.ReferenceField(SchemaDefinition)
    object_label = dockit.CharField(blank=True)
    view_points = dockit.ListField(dockit.SchemaField(ViewPoint), blank=True)
    #TODO add field for describing the label
    
    def save(self, *args, **kwargs):
        ret = super(Collection, self).save(*args, **kwargs)
        self.register_collection()
        #self.register_view_points()
        return ret
    
    def get_collection_name(self):
        return 'dockitcms.virtual.%s' % self.key
    
    def register_collection(self):
        from common import dockit_field_for_form_field
        name = str(self.key)
        form_fields = self.schema_definition.get_schema_fields()
        fields = SortedDict()
        for key, form_field in form_fields.iteritems():
            field = dockit_field_for_form_field(form_field)
            fields[key] = field
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

