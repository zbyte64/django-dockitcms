from django.contrib import admin
from django import forms

from fieldmaker.spec_widget import ListFormField, MetaFormMixin
from fieldmaker.admin.forms import FieldEntryForm
from fieldmaker.resource import field_registry

from dockit.admin.documentadmin import DocumentAdmin
from dockit.forms import DocumentForm

from models import SchemaDefinition, Collection, ViewPoint

class AdminSchemaDefinitionForm(DocumentForm, MetaFormMixin):
    data = ListFormField(form=FieldEntryForm)
    
    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        self.field_forms = dict()
        self.widget_forms = dict()
        for key, entry in field_registry.fields.iteritems():
            self.field_forms[key] = entry.render_for_admin(key)
        for key, entry in field_registry.widgets.iteritems():
            self.widget_forms[key] = entry.render_for_admin(key)
        self.post_form_init()
    
    class Meta:
        document = SchemaDefinition

class SchemaDefinitionAdmin(DocumentAdmin):
    form_class = AdminSchemaDefinitionForm

admin.site.register([SchemaDefinition], SchemaDefinitionAdmin)

class CollectionAdmin(DocumentAdmin):
    pass

admin.site.register([Collection], CollectionAdmin)

class ViewPointAdmin(DocumentAdmin):
    pass

admin.site.register([ViewPoint], ViewPointAdmin)
