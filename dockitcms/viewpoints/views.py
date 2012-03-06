from django.views.generic.base import TemplateResponseMixin
from django.template import Template, Context
from django.utils.safestring import mark_safe

from exceptions import HttpException

class VPEventFunction(object):
    def __init__(self, func, view, definition):
        self.func = func
        self.view = view
        self.definition = definition
    
    def __call__(self, *args, **kwargs):
        ret = self.func(*args, **kwargs)
        event = self.definition['event']
        event_kwargs = {self.definition['keyword']: ret}
        self.view.send_view_point_event(event, **event_kwargs)
        return ret

class VPViewMixin(object): #should be mixed into all view classes by view points
    view_point = None
    
    def get_scopes(self):
        return self.view_point.get_scopes()
    
    def send_view_point_event(self, event, **kwargs):
        return self.view_point.send_view_point_event(event, self, kwargs)
    
    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        self.request = request
        self.args = args
        self.kwargs = kwargs
        try:
            self.send_view_point_event('dispatch', request=request, args=args, kwargs=kwargs, handler=handler)
            return handler(request, *args, **kwargs)
        except HttpException, error:
            return error.response
    
    #on the return of the following functions at the top level, fire the event
    view_point_function_events = {
        'get_object':
            {'event': 'object',
             'keyword': 'object',},
        'get_context_data':
            {'event': 'context',
             'keyword': 'context',},
        'render_to_response':
            {'event': 'response',
             'keyword': 'response',},
        'get_queryset':
            {'event': 'queryset',
             'keyword': 'queryset',},
        'get_scopes':
            {'event': 'scopes',
             'keyword': 'scopes',},
         'get_template_names':
            {'event': 'template_names',
             'keyword': 'template_names'},
    }
    
    def __getattribute__(self, name):
        function_events = object.__getattribute__(self, 'view_point_function_events')
        ret = object.__getattribute__(self, name)
        if name in function_events:
            return VPEventFunction(ret, self, function_events[name])
        return ret

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

