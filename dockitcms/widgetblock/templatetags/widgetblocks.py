from django import template

register = template.Library()

from classytags.core import Options
from classytags.helpers import InclusionTag
from classytags.arguments import Argument

import collections

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
            return []
            #TODO possibly use DefaultScopeMiddleware to populate this
        for scope in scopes:
            if 'widgets' in scope.data:
                scope_widgets = list()
                for widget in scope.data['widgets'].data:
                    if widget.block_key == block_key:
                        widget.scope = scope
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

class RenderWidgets(InclusionTag):
    name = 'renderwidgets'
    template = 'widgetblock/widget_holder.html'
    options = Options(
        Argument('widgets', resolve=True),
    )
        
    def get_context(self, context, widgets):
        if not isinstance(widgets, collections.Iterable):
            widgets = [widgets]
        for widget in widgets:
            widget.rendered_content = widget.render(context)
        return {'widgets':widgets,}

register.tag(RenderWidgets)

