from django.views.generic.base import TemplateResponseMixin
from django.template import Template

class ConfigurableTemplateResponseMixin(TemplateResponseMixin):
    """
    A mixin that can be used to render a template.
    """
    configuration = None

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a response with a template rendered with the given context.
        """
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
