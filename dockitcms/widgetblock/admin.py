from django.contrib import admin
from django.views.generic import View
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect

from models import ModelWidgets

from dockitcms.admin.common import AdminAwareDocumentAdmin, AdminAwareSchemaAdmin

from dockit.admin.views import DocumentViewMixin

class GetOrCreateView(DocumentViewMixin, View):
    #title = _('Delete')
    key = 'lookup'
    
    @classmethod
    def get_url_pattern(cls, document_admin):
        return r'^lookup/(?P<app_label>.+)\.(?P<module_name>.+)\.(?P<pk>.+)/$'
    
    def get(self, request, *args, **kwargs):
        ct = ContentType.objects.get(app_label=kwargs['app_label'], model=kwargs['module_name'])
        try:
            obj = self.document.objects.get(content_type=ct, object_id=kwargs['pk'])
        except self.document.DoesNotExist:
            obj = self.document(content_type=ct, object_id=kwargs['pk'])
            obj.save()
        return HttpResponseRedirect(self.admin.reverse(self.admin.app_name+'_change', obj.pk))

class ModelWidgetsAdmin(AdminAwareDocumentAdmin):
    list_display = ['content_type', 'object_id']
    detail_views = AdminAwareDocumentAdmin.detail_views + [GetOrCreateView]

admin.site.register([ModelWidgets], ModelWidgetsAdmin)

class WidgetAdmin(AdminAwareSchemaAdmin):
    list_display = ['__str__', 'block_key', 'widget_type']

