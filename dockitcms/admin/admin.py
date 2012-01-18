from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from django.utils.functional import update_wrapper

from dockit.admin.documentadmin import DocumentAdmin
from dockit.admin.views import SingleObjectFragmentView

from dockitcms.models import SchemaDefinition, Collection

from forms import AdminSchemaDefinitionForm, AdminViewPointForm
from views import ManageCollectionView

class SchemaDefinitionAdmin(DocumentAdmin):
    form_class = AdminSchemaDefinitionForm

admin.site.register([SchemaDefinition], SchemaDefinitionAdmin)

class ViewPointInline(SingleObjectFragmentView):
    form_class = AdminViewPointForm
    template_name = 'admin/dockitcms/viewpoint/change_form.html'

class CollectionAdmin(DocumentAdmin):
    manage_collection = ManageCollectionView
    list_display = ['title', 'admin_manage_link']
    inline_views = [('^view_points\.[\d]+$', ViewPointInline)]
    
    def get_extra_urls(self):
        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.as_view(view, cacheable)(*args, **kwargs)
            return update_wrapper(wrapper, view)
        init = {'admin':self, 'admin_site':self.admin_site}
        return patterns('',
            url(r'^(?P<pk>.+)/manage/',
                wrap(self.manage_collection.as_view(**init)),
                name=(self.app_name+'_manage')),
        )

admin.site.register([Collection], CollectionAdmin)

#class ViewPointAdmin(DocumentAdmin):
#    form_class = AdminViewPointForm
#
#admin.site.register([ViewPoint], ViewPointAdmin)
