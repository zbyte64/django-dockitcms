from django.contrib import admin

from models import SiteWidgets

from dockitcms.admin.common import AdminAwareDocumentAdmin

class SiteWidgetsAdmin(AdminAwareDocumentAdmin):
    list_display = ['site']

admin.site.register([SiteWidgets], SiteWidgetsAdmin)
