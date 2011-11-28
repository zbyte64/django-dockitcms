from django.views.generic import View
from dockit.admin.documentadmin import DocumentAdmin

from dockitcms.models import Collection
from dockitcms.common import CMSURLResolver

class ManageCollectionView(View):
    admin = None
    admin_site = None
    
    def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        admin = self.get_document_admin()
        base_url = self.admin.reverse(self.admin.app_name+'_manage', *args, **kwargs)
        resolver = CMSURLResolver(r'^'+base_url, admin.get_urls())
        view_match = resolver.resolve(request.path)
        return view_match.func(request, *view_match.args, **view_match.kwargs)
    
    def get_document_admin(self):
        collection = self.get_collection()
        #TODO pass in a wrapped admin_site that handles reverse
        return DocumentAdmin(collection.get_document(), self.admin_site)
    
    def get_collection(self):
        return Collection.objects.get(self.kwargs['pk'])

