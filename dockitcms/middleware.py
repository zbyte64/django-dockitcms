from django.http import Http404
from django.conf import settings
from django.core.urlresolvers import get_script_prefix
from django.template.response import TemplateResponse

from models import ViewPoint

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
        for view_point in ViewPoint.objects.all():
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
