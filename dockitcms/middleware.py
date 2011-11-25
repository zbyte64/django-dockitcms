from django.http import Http404
from django.conf import settings
from django.core.urlresolvers import get_script_prefix
from django.template.response import TemplateResponse

from models import ViewPoint

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
        try:
            #TODO find a more efficient way to do this
            for view_point in ViewPoint.objects.all():
                if chomped_url.startswith(view_point.url):
                    try:
                        response = view_point.dispatch(request)
                    except Http404:
                        pass
                    else:
                        break
            if isinstance(response, TemplateResponse):
                response.render()
            return response
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except:
            if settings.DEBUG:
                raise
            return response

