from django.contrib import admin

from dockitcms.admin import AdminAwareDocumentAdmin

from models import BaseWidget

class WidgetAdmin(AdminAwareDocumentAdmin):
    list_display = ['__str__', 'bucket_key', 'vary_on']

admin.site.register([BaseWidget], WidgetAdmin)

