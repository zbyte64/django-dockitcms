from dockitcms.models import create_document_mixin
from dockitcms.mixins import SchemaExtensionMixin

from dockit import schema

from django.utils import unittest

MIXINS = {}

class MockedDocument(schema.Document, create_document_mixin(MIXINS)):
    seen_events = []
    
    def send_mixin_event(self, event, kwargs):
        result = super(MockedDocument, self).send_mixin_event(event, kwargs)
        self.seen_events.append({'event':event, 'kwargs':kwargs, 'result':result})
        return result

class SimpleSchema(schema.Schema):
    a_field = schema.CharField()

class SampleSchemaMixin(SchemaExtensionMixin):
    schema_class = SimpleSchema

MockedDocument.register_mixin('test', SampleSchemaMixin)

class MixinTest(unittest.TestCase):
    def create_test_document(self, **kwargs):
        MockedDocument.seen_events = []
        document = MockedDocument.to_python(kwargs, parent=None)
        document.save()
        assert hasattr(MockedDocument, 'send_mixin_event')
        assert hasattr(document, 'send_mixin_event'), str(getattr(document, 'send_mixin_event', None)) + str(dir(document))
        return document
    
    def get_admin_for_document(self, document):
        from django.contrib.admin import site
        from dockitcms.admin import AdminAwareDocumentAdmin
        return AdminAwareDocumentAdmin(document, site, schema=document)
    
    def test_mixin_expands_document(self):
        document = self.create_test_document(mixins=['test'], a_field='Hello world')
        self.assertTrue(hasattr(document, 'a_field'))
        self.assertEqual(document.a_field, 'Hello world')
        
        #ensure our mixin hasn't contaminated the original
        document = self.create_test_document()
        self.assertFalse(hasattr(document, 'a_field'))
    
    def test_mixin_sends_admin_signal(self):
        document = self.create_test_document(mixins=['test'], a_field='Hello world')
        admin = self.get_admin_for_document(document)
        self.assertTrue(hasattr(document, 'send_mixin_event'))
        self.assertTrue(hasattr(admin.schema, 'send_mixin_event'))
        self.assertTrue('a_field' in admin.get_excludes())
        admin.get_inline_instances()
        events = [event['event'] for event in MockedDocument.seen_events]
        self.assertTrue('admin.excludes' in events, '%s not in %s' % ('admin.excludes', events))
        self.assertTrue('admin.inline_instances' in events, '%s not in %s' % ('admin.inline_instances', events))

