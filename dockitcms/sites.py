from django.conf.urls.defaults import patterns, url, include
from django.conf import settings

from dockitcms.models import BaseViewPoint, Subsite, Collection, Index
from dockitcms.signals import pre_init_applications, post_init_applications, post_reload_site

class DockitCMSSite(object):
    def __init__(self, name=None, app_name='dockitcms_app'):
        self.root_path = None
        if name is None:
            self.name = 'dockitcms'
        else:
            self.name = name
        self.app_name = app_name
        self.registered_view_points = set()
    
    def get_urls(self): #CONSIDER, won't this match everything?!?
        urlpatterns = patterns('',)
        
        for subsite in Subsite.objects.filter(sites=settings.SITE_ID):
            base_url = subsite.url
            if base_url.startswith('/'):
                base_url = base_url[1:]
            urlpatterns += patterns('',
                url(r'^%s' % base_url, include(subsite.urls))
            )
        return urlpatterns

    @property
    def urls(self):
        self.init_applications()
        return self#, self.app_name, self.name
    
    @property
    def urlpatterns(self):
        if not hasattr(self, '_urlpatterns'):
            self._urlpatterns = self.get_urls()
        return self._urlpatterns
    
    def init_applications(self):
        pre_init_applications.send(sender=type(self), cms_site=self)
        
        errors = list()
        for collection in Collection.objects.all():
            try:
                collection.register_collection()
            except Exception, err:
                print err
                errors.append(err)
        for view_point in BaseViewPoint.objects.all():
            try:
                view_point.register_view_point()
            except Exception, err:
                print err
                errors.append(err)
        for index in Index.objects.all():
            try:
                index.register_index()
            except Exception, err:
                print err
                errors.append(err)
        post_init_applications.send(sender=type(self), cms_site=self, errors=errors)
    
    def reload_site(self):
        if hasattr(self, '_urlpatterns'):
            del self._urlpatterns
        self.init_applications()
        post_reload_site.send(sender=self, cms_site=self)

site = DockitCMSSite()

import dockitcms.listeners

