from dockit import schema

from dockitcms.scope import ScopeList, Scope, get_site_scope
from dockitcms.models.mixin import create_document_mixin, ManageUrlsMixin

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns, url, include


SUBSITE_MIXINS = {}
VIEW_POINT_MIXINS = {}

class Subsite(schema.Document, ManageUrlsMixin, create_document_mixin(SUBSITE_MIXINS)):
    url = schema.CharField()
    name = schema.CharField()
    sites = schema.ModelSetField(Site, blank=True)
    
    def __unicode__(self):
        return u'%s - %s' % (self.name, self.url)
    
    def get_urls(self):
        urlpatterns = patterns('',)
        
        for view_point in BaseViewPoint.objects.filter(subsite=self):
            urlpatterns += patterns('',
                url(r'', include(view_point.urls))
            )
        return urlpatterns
    
    @property
    def urls(self):
        #urls, app_name, namespace
        return self, self.name, None
    
    @property
    def urlpatterns(self):
        return self.get_urls()

Subsite.objects.index('sites').commit()

class BaseViewPoint(schema.Document, ManageUrlsMixin, create_document_mixin(VIEW_POINT_MIXINS)):
    subsite = schema.ReferenceField(Subsite)
    
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
        
        return ScopeList([site_scope, subsite_scope, viewpoint_scope])
    
    def get_admin_view(self, **kwargs):
        from dockitcms.admin.views import ViewPointDesignerFragmentView
        kwargs['view_spec'] = self
        return ViewPointDesignerFragmentView.as_view(**kwargs)
    
    def get_urls(self):
        raise NotImplementedError
    
    def get_absolute_url(self):
        return self.reverse('index')
    
    @property
    def urls(self):
        return self, None, self.pk
    
    @property
    def urlpatterns(self):
        return self.get_urls()
    
    def reverse(self, name, *args, **kwargs):
        if not name.startswith('dockitcms:%s:' % self.pk):
            name = 'dockitcms:%s:%s' % (self.pk, name)
        try:
            return reverse(name, args=args, kwargs=kwargs)#, current_app=self.subsite.name)
        except Exception, error:
            print error
            raise
    
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
    
    @property
    def url_regexp(self):
        url = self.url
        if url.startswith('/'):
            url = url[1:]
        if not url.startswith('^'):
            url = '^'+url
        return r'%s' % url
    
    def get_urls(self):
        urlpatterns = patterns('',
            (self.url_regexp, include(self.get_inner_urls())),
        )
        return urlpatterns
    
    def get_inner_urls(self):
        return patterns('',)
    
    def __unicode__(self):
        if self.url:
            return self.url
        else:
            return self.__repr__()
    
    class Meta:
        proxy = True

