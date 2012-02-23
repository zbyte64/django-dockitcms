from django.views.generic import View

from common import AdminAwareDocumentAdmin

from dockitcms.models import Collection
from dockitcms.common import CMSURLResolver

from dockit.admin.breadcrumbs import Breadcrumb

class VirtualDocumentAdmin(AdminAwareDocumentAdmin):
    def __init__(self, document, admin_site, base_url):
        AdminAwareDocumentAdmin.__init__(self, document, admin_site)
        self.base_url = base_url
        self.resolver = CMSURLResolver(r'^'+base_url, self.get_urls())
    
    def reverse(self, name, *args, **kwargs):
        ret = self.resolver.reverse(name, *args, **kwargs)
        return self.base_url + ret
    
    def get_base_breadcrumbs(self):
        admin_name = self.admin_site.name
        model_name = self.model._meta.verbose_name
        opts = self.model._meta
        breadcrumbs = [
            Breadcrumb('Home', ['%s:index' % admin_name]),
            Breadcrumb(opts.app_label, ['%s:index' % admin_name]), #TODO app listing support
            Breadcrumb(opts.verbose_name_plural, self.reverse('%s_changelist' % self.app_name)),
        ]
        return breadcrumbs

class ManageCollectionView(View):
    admin = None
    admin_site = None
    
    def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        admin = self.get_document_admin()
        view_match = admin.resolver.resolve(request.path)
        return view_match.func(request, *view_match.args, **view_match.kwargs)
    
    def get_document_admin(self):
        collection = self.get_collection()
        base_url = self.admin.reverse(self.admin.app_name+'_manage', *self.args, **self.kwargs)
        return VirtualDocumentAdmin(collection.get_document(), self.admin_site, base_url)
    
    def get_collection(self):
        return Collection.objects.get(pk=self.kwargs['pk'])

