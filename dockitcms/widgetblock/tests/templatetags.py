from dockitcms.widgetblock.templatetags.widgetblocks import WidgetBlock, RenderWidgets
from dockitcms.widgetblock.common import WidgetBlockScopeDisplay


from dockitcms.scope import Scope, ScopeList

from django.utils import unittest

class MockedScope(Scope):
    processors = []
    
    def get_scope_processors(self):
        return self.processors

class MockWidget(object):
    block_key = 'testblock'
    
    def render(self, context):
        return 'pass'

class TestableWidgetBlock(WidgetBlock):
    def __init__(self):
        pass

class TestableRenderWidgets(RenderWidgets):
    def __init__(self):
        pass

class WidgetBlockTest(unittest.TestCase):
    def setUp(self):
        self.block = TestableWidgetBlock()
    
    def get_context(self):
        scope = Scope('object')
        self.mock_widget = MockWidget()
        scope.add_data('widgets', [self.mock_widget])
        context = {'scopes': ScopeList([scope])}
        return context
    
    def test_get_widgets(self):
        context = self.get_context()
        block_key = 'testblock'
        returned_widgets = self.block.get_widgets(context, block_key)
        self.assertTrue(self.mock_widget in returned_widgets, str(returned_widgets))
        self.assertTrue('widgetblocks' in context['scopes'].info)
        self.assertTrue('testblock' in context['scopes'].info['widgetblocks'].blocks_seen)
    
    def test_get_context(self):
        context = self.get_context()
        block_key = 'testblock'
        widget_context = self.block.get_context(context, block_key)
        self.assertEqual(widget_context['block_key'], block_key)
        self.assertEqual(len(widget_context['widgets']), 1)
        self.assertTrue(getattr(self.mock_widget, 'rendered_content', None))

class RenderWidgetsTest(unittest.TestCase):
    def setUp(self):
        self.block = TestableRenderWidgets()
        self.mock_widget = MockWidget()
    
    def test_get_context_handles_empty_data(self):
        self.block.get_context({}, [])
    
    def test_get_context(self):
        context = self.block.get_context({}, [self.mock_widget])
        self.assertTrue('widgets' in context)
        self.assertTrue(self.mock_widget in context['widgets'])
        self.assertTrue(getattr(self.mock_widget, 'rendered_content', None))

class WidgetBlockDisplayTest(unittest.TestCase):
    def setUp(self):
        self.display = WidgetBlockScopeDisplay()
    
    def test_add_block(self):
        self.display.add_block('testblock')
        self.assertTrue('testblock' in self.display.blocks_seen)
    
    def test_render(self):
        self.display.render({})

