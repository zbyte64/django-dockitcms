from django import template

register = template.Library()

from classytags.core import Options
from classytags.helpers import InclusionTag
from classytags.arguments import Argument

class ViewScope(InclusionTag):
    name = 'viewscope'
    template = 'dockitcms/templatetags/viewscope.html'
    #options = Options(
    #    Argument('block_key', resolve=True),
    #)
    
    def get_context(self, context):
        return {'scopes': context.get('scopes', [])}

register.tag(ViewScope)
