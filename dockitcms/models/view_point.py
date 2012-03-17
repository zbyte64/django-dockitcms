from dockit import schema

from dockitcms.scope import Scope, get_site_scope

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

import re
import urlparse

from mixin import create_document_mixin

SUBSITE_MIXINS = {}
VIEW_POINT_MIXINS = {}

class ManageUrlsMixin(object):
    def get_manage_urls(self):
        admin_name = '_'.join((self._meta.app_label, self._meta.module_name))
        urls = {'add': reverse('admin:%s_add' % admin_name),
                'list': reverse('admin:%s_changelist' % admin_name),}
        if self.pk:
            urls['edit'] = reverse('admin:%s_change' % admin_name, args=[self.pk])
        return urls

class Subsite(schema.Document, ManageUrlsMixin, create_document_mixin(SUBSITE_MIXINS)):
    url = schema.CharField()
    name = schema.CharField()
    sites = schema.ModelSetField(Site, blank=True)
    
    def __unicode__(self):
        return u'%s - %s' % (self.name, self.url)

Subsite.objects.index('sites').commit()

class BaseViewPoint(schema.Document, ManageUrlsMixin, create_document_mixin(VIEW_POINT_MIXINS)):
    subsite = schema.ReferenceField(Subsite)
    
    def contains_url(self, url):
        raise NotImplementedError
    
    def _base_url(self):
        return self.subsite.url
    base_url = property(_base_url)
    
    #TODO this is currently only called during the save
    def register_view_point(self):
        pass
    
    def send_view_point_event(self, event, view, kwargs):
        '''
        The view calls this to notify the mixins that an event has happened
        '''
        mixins = self.get_active_mixins(self)
        results = []
        for mixin_cls in mixins:
            if not hasattr(mixin_cls, 'handle_view_point_event'):
                continue
            mixin = mixin_cls(_primitive_data=self._primitive_data)
            val = mixin.handle_view_point_event(event, view, kwargs)
            results.append((mixin, val))
        return results
    
    def get_scopes(self):
        site_scope = get_site_scope()
        
        subsite_scope = Scope('subsite', object=self.subsite)
        subsite_scope.add_data('object', self.subsite, self.subsite.get_manage_urls())
        
        viewpoint_scope = Scope('viewpoint', object=self)
        viewpoint_scope.add_data('object', self, self.get_manage_urls())
        
        return [site_scope, subsite_scope, viewpoint_scope]
    
    def get_admin_view(self, **kwargs):
        from dockitcms.admin.views import ViewPointDesignerFragmentView
        kwargs['view_spec'] = self
        return ViewPointDesignerFragmentView.as_view(**kwargs)
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns
        return patterns('')
    
    def get_resolver(self):
        from dockitcms.common import CMSURLResolver
        urls = self.get_urls()
        return CMSURLResolver(r'^'+self.base_url, urls)
    
    def dispatch(self, request):
        resolver = self.get_resolver()
        view_match = resolver.resolve(request.path)
        return view_match.func(request, *view_match.args, **view_match.kwargs)
    
    def reverse(self, name, *args, **kwargs):
        resolver = self.get_resolver()
        return self.base_url + resolver.reverse(name, *args, **kwargs)
    
    def save(self, *args, **kwargs):
        super(BaseViewPoint, self).save(*args, **kwargs)
        self.register_view_point()
    
    class Meta:
        typed_field = 'view_type'
        verbose_name = 'View Point'
        collection = 'dockitcms.viewpoint'

BaseViewPoint.objects.index('subsite').commit()

class ViewPoint(BaseViewPoint):
    url = schema.CharField(help_text='May be a regular expression that the url has to match')
    
    def contains_url(self, url):
        return bool(self.url_regexp.match(url))
    
    @property
    def url_regexp(self):
        return re.compile(self.base_url)
    
    def _base_url(self):
        return urlparse.urljoin(self.subsite.url, self.url)
    base_url = property(_base_url)
    
    def get_absolute_url(self):
        return self.base_url
    
    def __unicode__(self):
        if self.url:
            return self.url
        else:
            return self.__repr__()
    
    class Meta:
        proxy = True

