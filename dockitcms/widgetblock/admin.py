from django.contrib import admin

from models import ModelWidgets

from dockitcms.admin.common import AdminAwareDocumentAdmin, AdminAwareSchemaAdmin

class ModelWidgetsAdmin(AdminAwareDocumentAdmin):
    list_display = ['content_type', 'object_id']
    #TODO need a get or create view for and object

admin.site.register([ModelWidgets], ModelWidgetsAdmin)

class WidgetAdmin(AdminAwareSchemaAdmin):
    list_display = ['__str__', 'block_key', 'widget_type']

