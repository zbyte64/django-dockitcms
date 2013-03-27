from dockitcms.middleware import DefaultScopeMiddleware
from dockitcms.scope import ScopeList

from django.utils import unittest
from django.test.client import RequestFactory

class MockedTemplateResponse(object):
    def __init__(self):
        self.context_data = {}

class DefaultScopeMiddlewareTest(unittest.TestCase):
    def setUp(self):
        self.middleware = DefaultScopeMiddleware()
        self.factory = RequestFactory()
    
    def test_process_template_response(self):
        request = self.factory.get('/')
        response = MockedTemplateResponse()
        new_response = self.middleware.process_template_response(request, response)
        self.assertEqual(response, new_response)
        self.assertTrue('scopes' in response.context_data)
        self.assertTrue(isinstance(response.context_data['scopes'], ScopeList))
        #TODO test site scope is in
        #TODO test object level scoping

