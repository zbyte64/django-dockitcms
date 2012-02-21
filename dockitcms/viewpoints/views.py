from django.views.generic.base import TemplateResponseMixin
from django.template import Template, Context
from django.utils.safestring import mark_safe

class VPViewMixin(object): #should be mixed into all view classes by view points
    view_point = None
    
    def get_scopes(self):
        return self.view_point.get_scopes()
    
    #TODO permissions

class ConfigurableTemplateResponseMixin(VPViewMixin, TemplateResponseMixin):
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
        context['scopes'] = self.get_scopes()
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
