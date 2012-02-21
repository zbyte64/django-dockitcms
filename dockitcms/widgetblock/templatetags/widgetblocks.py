from django import template

register = template.Library()

from classytags.core import Options
from classytags.helpers import InclusionTag
from classytags.arguments import Argument

import dockit

class WidgetBlock(InclusionTag):
    name = 'widgetblock'
    template = 'widgetblock/widget_holder.html'
    options = Options(
        Argument('block_key', resolve=True),
    )
    
    def get_widgets(self, context, block_key):
        widgets = list()
        scopes = context['scopes']
        for scope in scopes:
            if 'object' in scope.kwargs:
                obj = scope.kwargs['object']
                scope_widgets = list()
                if isinstance(obj, dockit.Schema) and hasattr(obj, '_widgets'):
                    for widget in obj._widgets:
                        if widget.block_key == block_key:
                            scope_widgets.append(widget)
                if scope_widgets: #TODO how to properly merge
                    widgets.extend(scope_widgets)
        return widgets
    
    def get_context(self, context, block_key):
        widgets = list(self.get_widgets(context, block_key))
        for widget in widgets:
            widget.rendered_content = widget.render(context)
        return {'widgets':widgets,
                'block_key':block_key,}

register.tag(WidgetBlock)
