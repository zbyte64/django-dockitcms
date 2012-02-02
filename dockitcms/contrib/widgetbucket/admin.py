from django.contrib import admin

from dockit.admin.documentadmin import DocumentAdmin

from models import BaseWidget

class WidgetAdmin(DocumentAdmin):
    list_display = ['__str__', 'bucket_key', 'vary_on']

admin.site.register([BaseWidget], WidgetAdmin)
