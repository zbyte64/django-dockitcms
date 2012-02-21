from django import template

register = template.Library()

from classytags.core import Options
from classytags.helpers import InclusionTag
from classytags.arguments import Argument

from dockitcms.scope import get_site_scope

class WidgetBlock(InclusionTag):
    name = 'widgetblock'
    template = 'widgetblock/widget_holder.html'
    options = Options(
        Argument('block_key', resolve=True),
    )
    
    def get_widgets(self, context, block_key):
        widgets = list()
        if 'scopes' in context:
            scopes = context['scopes']
        else:
            scopes = [get_site_scope()]
        for scope in scopes:
            if 'object' in scope.kwargs:
                obj = scope.kwargs['object']
                scope_widgets = list()
                if hasattr(obj, '_widgets'):
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
