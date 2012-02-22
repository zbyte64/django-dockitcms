from django.contrib import admin

from models import SiteWidgets

from dockitcms.admin.common import AdminAwareDocumentAdmin, AdminAwareSchemaAdmin

class SiteWidgetsAdmin(AdminAwareDocumentAdmin):
    list_display = ['site']

admin.site.register([SiteWidgets], SiteWidgetsAdmin)

class WidgetAdmin(AdminAwareSchemaAdmin):
    list_display = ['__str__', 'block_key', 'widget_type']

