from django.http import Http404
from django.conf import settings
from django.core.urlresolvers import get_script_prefix
from django.template.response import TemplateResponse

from models import ViewPoint, Subsite
from scope import get_site_scope, Scope

registered_view_points = set()

class DockitCMSMiddleware(object):
    ignore_script_prefix = False
    
    def process_response(self, request, response):
        if response.status_code != 404:
            return response # No need to check for a flashpage for non-404 responses.
        url = request.path_info
        chomped_url = url
        if self.ignore_script_prefix:
            prefix = None
        else:
            prefix = get_script_prefix()
        
        if prefix and chomped_url.startswith(prefix):
            chomped_url = chomped_url[len(prefix)-1:]
        
        #TODO find a more efficient way to do this
        subsites = Subsite.objects.filter(sites=settings.SITE_ID)
        for subsite in subsites:
            view_points = ViewPoint.objects.filter(subsite=subsite)
            for view_point in view_points:
                if view_point.url_regexp.match(chomped_url):
                    if view_point.pk not in registered_view_points:
                        view_point.register_view_point()
                        registered_view_points.add(view_point.pk)
                    try:
                        response = view_point.dispatch(request)
                    except Http404:
                        pass
                    else:
                        if isinstance(response, TemplateResponse):
                            response.render()
                        return response
        return response

class DefaultScopeMiddleware(object):
    def process_template_response(self, request, response):
        context = response.context_data
        if 'scopes' not in context:
            context['scopes'] = [get_site_scope()]
            if 'object' in context and not any([scope.name == 'object' for scope in context['scopes']]):
                context['scopes'].append(Scope(name='object', object=context['object']))
        return response
