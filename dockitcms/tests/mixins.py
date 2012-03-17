from dockitcms.models import create_document_mixin
from dockitcms.mixins import SchemaExtensionMixin

from dockit import schema

from django.utils import unittest

MIXINS = {}

class MockedDocument(create_document_mixin(MIXINS)):
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
        collection = MockedDocument.to_python(kwargs, parent=None)
        collection.save()
        return collection
    
    def test_mixin_expands_document(self):
        document = self.create_test_document(mixins=['test'], a_field='Hello world')
        self.assertTrue(hasattr(document, 'a_field'))
        self.assertEqual(document.a_field, 'Hello world')
        
        #ensure our mixin hasn't contaminated the original
        document = self.create_test_document()
        self.assertFalse(hasattr(document, 'a_field'))

