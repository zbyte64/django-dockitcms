from dockitcms.models import Collection, Application
from dockitcms.fields import CharField
from dockitcms.mixins import AdminObjectToolMixin, AdminInlineMixin, AdminFormMixin

from dockit import schema

from django.utils import unittest

class MockedCollection(Collection):
    active_mixins = []
    seen_events = []
    
    def send_mixin_event(self, event, kwargs):
        result = Collection.send_mixin_event(self, event, kwargs)
        self.seen_events.append({'event':event, 'kwargs':kwargs, 'result':result})
        return result
    
    def get_active_mixins(self):
        return [mixin(self) for mixin in self.active_mixins]
    
    class Meta:
        proxy = True

class SimpleSchema(schema.Schema):
    a_field = schema.CharField()

class InlineSchema(schema.Schema):
    a_list = schema.ListField(schema.SchemaField(SimpleSchema), blank=True)

class SampleObjectToolMixin(AdminObjectToolMixin):
    schema_class = InlineSchema

class SampleAdminInlineMixin(AdminInlineMixin):
    schema_class = InlineSchema

class SampleAdminFormMixin(AdminFormMixin):
    schema_class = SimpleSchema

class CollectionTest(unittest.TestCase):
    def setUp(self):
        app = Application(name='test')
        app.save()
        self.application = app
    
    def get_admin_for_document(self, document):
        from django.contrib.admin import site
        from dockitcms.admin import AdminAwareDocumentAdmin
        return AdminAwareDocumentAdmin(document, site, schema=document)
    
    def create_test_collection(self, **kwargs):
        MockedCollection.active_mixins = []
        active_mixins = kwargs.pop('active_mixins', [])
        params = {'application':self.application,
                  'key':'testcollection',
                  'title':'Test Collection',
                  'fields':[CharField(name='title', null=False, blank=True)],}
        params.update(kwargs)
        collection = MockedCollection(**params)
        collection.active_mixins = active_mixins
        collection.seen_events = []
        collection.save()
        return collection
    
    def test_collection_creates_document(self):
        collection = self.create_test_collection()
        
        document = collection.get_document()
        self.assertTrue('title' in document._meta.fields)
    
    def test_collection_mixin_signals(self):
        collection = self.create_test_collection()
        document = collection.get_document()
        admin = self.get_admin_for_document(document)
        admin.get_excludes()
        admin.get_inline_instances()
        events = [event['event'] for event in collection.seen_events]
        self.assertTrue('admin.excludes' in events, '%s not in %s' % ('admin.excludes', events))
        self.assertTrue('admin.inline_instances' in events, '%s not in %s' % ('admin.inline_instances', events))
    
    def test_collection_admin_objectool_mixin(self):
        collection = self.create_test_collection(active_mixins=[SampleObjectToolMixin])
        document = collection.get_document()
        admin = self.get_admin_for_document(document)
        self.assertTrue('a_list' in admin.get_excludes())
        for inline in admin.get_inline_instances():
            self.assertFalse(inline.dotpath.startswith('a_list'))
    
    def test_collection_admin_inline_mixin(self):
        collection = self.create_test_collection(active_mixins=[SampleAdminInlineMixin])
        document = collection.get_document()
        admin = self.get_admin_for_document(document)
        self.assertTrue('a_list' in admin.get_excludes())
        
        seen = False
        for inline in admin.get_inline_instances():
            if inline.dotpath.startswith('a_list'):
                seen = True
                break
        self.assertTrue(seen, 'Inline mixin failed to create an inline')
    
    def test_collection_admin_form_mixin(self):
        collection = self.create_test_collection(active_mixins=[SampleAdminFormMixin])
        document = collection.get_document()
        admin = self.get_admin_for_document(document)
        self.assertFalse('a_field' in admin.get_excludes())

