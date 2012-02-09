from django.views.generic.base import TemplateResponseMixin
from django.template import Template, Context
from django.template.loader import get_template
from django.utils.safestring import mark_safe

class ConfigurableTemplateResponseMixin(TemplateResponseMixin):
    """
    A mixin that can be used to render a template.
    """
    configuration = None
    
    def render_content(self, context):
        if 'content' in self.configuration:
            template = Template(self.configuration['content'])
            return mark_safe(template.render(Context(context)))
        return ''

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a response with a template rendered with the given context.
        """
        #TODO this should be view_point.content
        context['content'] = self.render_content(context)
        return self.response_class(
            request = self.request,
            template = self.get_template_names(),
            context = context,
            **response_kwargs
        )

    def get_template_names(self):
        if self.configuration['template_source'] == 'name':
            return [self.configuration['template_name']]
        if self.configuration['template_source'] == 'html':
            return Template(self.configuration['template_html'])
        assert False, str(self.configuration)

def _generate_context_for_scaffold(document):
    context = {'document':document,
               'fields':document._meta.fields,
               'lflt':'{{',
               'rflt':'}}',
               'ltag':'{%',
               'rtag':'%}',}
    return context

def generate_object_list_scaffold(document):
    context = _generate_context_for_scaffold(document)
    template = get_template('dockitcms/scaffold/object_list.html')
    return template.render(Context(context))

def generate_object_detail_scaffold(document):
    context = _generate_context_for_scaffold(document)
    template = get_template('dockitcms/scaffold/object_detail.html')
    return template.render(Context(context))

def prep_for_kwargs(dictionary):
    if hasattr(dictionary, 'to_primitive'):
        return dictionary.to_primitive(dictionary)
    result = dict()
    for key, value in dictionary.iteritems():
        result[str(key)] = value
    return result

