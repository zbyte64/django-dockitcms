from dockitcms.widgetblock.scope_processors import widgets, modelwidgets

from dockitcms.scope import Scope

from django.utils import unittest

class MockedScope(Scope):
    processors = []
    
    def get_scope_processors(self):
        return self.processors

class MockObject(object):
    widgets = []

class ScopesTest(unittest.TestCase):
    def test_widgets_scope(self):
        scope = MockedScope('view', object=MockObject())
        widgets(scope)
        self.assertTrue('widgets' in scope.data)
    
    def test_modelwidgets_scope(self):
        scope = MockedScope('view', object=MockObject())
        modelwidgets(scope)
        #TODO object=User
        #create some: ModelWidgets.objects.filter(content_type=ct, object_id=str(pk))
    
    
