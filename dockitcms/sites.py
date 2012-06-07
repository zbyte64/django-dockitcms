from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import Resolver404
from django.http import Http404
from django.conf import settings

from models import BaseViewPoint, Subsite

class DockitCMSSite(object):
    def __init__(self, name=None, app_name='dockitcms'):
        self.root_path = None
        if name is None:
            self.name = 'dockitcms'
        else:
            self.name = name
        self.app_name = app_name
        self.registered_view_points = set()
    
    def get_urls(self): #CONSIDER, won't this match everything?!?
        urlpatterns = patterns('',
            url(r'^(?P<path>.*)$',
                self.index,
                name='index'),
        )
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.name
    
    def index(self, request, path):
        subsites = Subsite.objects.filter(sites=settings.SITE_ID)
        for subsite in subsites:
            view_points = BaseViewPoint.objects.filter(subsite=subsite)
            for view_point in view_points:
                if view_point.contains_url(path):
                    if view_point.pk not in self.registered_view_points:
                        view_point.register_view_point()
                        self.registered_view_points.add(view_point.pk)
                    try:
                        response = view_point.dispatch(request)
                    except Resolver404:
                        pass
                    else:
                        return response
        msg = 'No matching view points'
        if not subsites:
            msg = 'No matching subsites'
        raise Http404(msg)

site = DockitCMSSite()

