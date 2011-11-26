from django.views.generic import View

class ManageCollectionView(View):
    admin = None
    admin_site = None
    
    def dispatch(self, request, *args, **kwargs):
        pass #TODO

