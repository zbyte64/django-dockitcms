from django.contrib import admin

from dockit.admin.documentadmin import DocumentAdmin, SchemaAdmin
from dockit.admin.inlines import TabularInline

from models import BaseWidget, CTAImage

class WidgetAdmin(DocumentAdmin):
    list_display = ['__str__', 'bucket_key', 'vary_on']

admin.site.register([BaseWidget], WidgetAdmin)

class CTAImageInline(TabularInline):
    schema = CTAImage
    dotpath = 'images'

class CTAWidgetAdmin(SchemaAdmin):
    pass#inlines = [CTAImageInline]

