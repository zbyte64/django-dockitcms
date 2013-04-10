# -*- coding: utf-8 -*-
import uuid

from django.utils.datastructures import SortedDict

from dockit import schema
from dockit.schema import get_base_document
from dockit.schema.loading import force_register_documents
from dockit.schema.schema import create_document

from dockitcms.models.design import SchemaEntry
from dockitcms.models.collection import Collection
from dockitcms.models.view_point import PublicResource


class TemplateEntry(schema.Schema):
    path = schema.CharField()
    source = schema.TextField() #TODO template validator
    js_files = schema.ListField(schema.FileField(upload_to='dockitcms/u-js/'), blank=True)
    css_files = schema.ListField(schema.FileField(upload_to='dockitcms/u-css/'), blank=True)

class PageDefinition(SchemaEntry):
    unique_id = schema.CharField(default=uuid.uuid4, editable=False)
    templates = schema.ListField(schema.SchemaField(TemplateEntry))

    def get_template(self, names):
        #TODO return from templates if any match else use system level call
        return None

class BasePage(schema.Schema):
    parent = schema.ReferenceField('self', blank=True, null=True)
    url = schema.CharField(blank=True)
    url_name = schema.SlugField(blank=True, help_text='registers the page with the url tag with this name')
    path = schema.CharField(editable=False)
    title = schema.CharField()
    slug = schema.SlugField()
    published = schema.BooleanField()
    template = schema.CharField()

    inline_css = schema.TextField(blank=True)
    inline_js = schema.TextField(blank=True)

    def clean_path(self):
        if self.url:
            return self.url
        if self.parent:
            return self.parent.path + self.slug + '/'
        return self.slug + '/'

class BasePageDefinition(schema.Schema):
    pass

'''
class WidgetPageDefinition(BasePageDefinition):
    widgets = schema.ListField(WidgetField())
'''

class PageCollection(Collection):
    title = schema.CharField()
    page_definitions = schema.ListField(schema.SchemaField(PageDefinition))

    def get_collection_name(self):
        return 'dockitcms.virtual.%s' % self.key

    def get_schema_name(self):
        return str(''.join([part for part in self.title.split()]))

    def register_collection(self):
        #create a base page document
        params = {
            'module': 'dockitcms.models.virtual',
            'virtual': False,
            'verbose_name': self.title,
            'collection': self.get_collection_name(),
            'parents': (BasePage, schema.Document),
            'name': self.get_schema_name(),
            'attrs': SortedDict(),
            'fields': SortedDict(),
            'typed_field': '_page_type',
        }
        if self.application:
            params['app_label'] = self.application.name
        params['attrs']['_collection_document'] = self

        base_doc = create_document(**params)
        force_register_documents(base_doc._meta.app_label, base_doc)
        base_doc.objects.index('path').commit()

        #loop through page_definitions and register them
        for page_def in self.page_definitions:
            params = {
                'parents': (base_doc,),
                'virtual': False,
                'typed_key': page_def.unique_id,
                'attrs': SortedDict([
                    ('_page_def', page_def),
                ])
            }
            page_def.get_document(**params)

        #CONSIDER: provide page defs defined in code
        for unique_id, page_schema in dict().items(): #REGISTERED_PAGE_DEFS.items()
            params = {
                'virtual': False,
                'typed_key': unique_id,
                'parents': (page_schema, base_doc),
                'name': '', #page_schema._meta.name,
                'fields': SortedDict(),
            }
            create_document(**params)

        return base_doc

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
        from dockitcms.pagecollection.resources import PageCollectionResource
        return PageCollectionResource

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
        typed_key = 'dockitcms.page'

class PublicPageCollectionResource(PublicResource):
    collection = schema.ReferenceField(PageCollection)
    #view_points = schema.ListField(schema.SchemaField(BaseViewPoint))

    @property
    def cms_resource(self):
        return self.collection.get_collection_resource()

    def get_public_resource_kwargs(self, **kwargs):
        #print 'get_collection_kwargs'
        from dockitcms.pagecollection.viewpoints import PageViewPoint
        kwargs['view_points'] = [
            PageViewPoint(page_resource=self)
        ]
        return super(PublicPageCollectionResource, self).get_public_resource_kwargs(**kwargs)

    class Meta:
        typed_key = 'pagecollection'
