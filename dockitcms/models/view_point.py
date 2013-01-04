from dockit import schema

from dockitcms.scope import ScopeList, Scope, get_site_scope
from dockitcms.models.mixin import create_document_mixin, ManageUrlsMixin

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.conf import settings


SUBSITE_MIXINS = {}
VIEW_POINT_MIXINS = {}

class Subsite(schema.Document, ManageUrlsMixin, create_document_mixin(SUBSITE_MIXINS)):
    url = schema.CharField()
    name = schema.CharField()
    slug = schema.SlugField()
    sites = schema.ModelSetField(Site, blank=True)
    
    def __unicode__(self):
        return u'%s - %s' % (self.name, self.url)
    
    def get_logger(self):
        from dockitcms.sites import logger
        return logger
    
    def get_site_client(self):
        """
        Returns a hyperadmin client for public consumption
        """
        from dockitcms.resources.virtual import site
        from dockitcms.resources.public import PublicSubsite
        from dockitcms.models import Collection
        
        subsite_api = PublicSubsite(api_endpoint=site, name=self.name)
        logger = self.get_logger()
        
        for view_point in BaseViewPoint.objects.filter(subsite=self):
            subsite_api.register_viewpoint(view_point)
        
        for collection in Collection.objects.all():
            subsite_api.register_collection(collection)
        
        return subsite_api
    
    def get_urls(self):
        if not hasattr(self, '_client'):
            self._client = self.get_site_client()
        client = self._client
        return client.get_urls()
    
    @property
    def urls(self):
        #urls, app_name, namespace
        try:
            self.urlpatterns
        except Exception as error:
            logger = self.get_logger()
            logger.exception('Error while constructing urls')
            raise
        return self, None, self.name
    
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
    
    def get_view_endpoints(self):
        """
        returns a list of tuples
        (collection, [(endpoint_cls, kwargs)...])
        """
        raise NotImplementedError
    
    def register_view_endpoints(self, site):
        pass
    
    def get_absolute_url(self):
        return self.reverse('index')
    
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
    
    def get_url(self):
        url = self.url or ''
        if url.startswith('/'):
            url = url[1:]
        if not url.startswith('^'):
            url = '^'+url
        return url
        
    def get_url_regexp(self):
        url = self.get_url()
        return r'%s' % url
    
    def __unicode__(self):
        if self.url:
            return self.url
        else:
            return self.__repr__()
    
    class Meta:
        proxy = True

